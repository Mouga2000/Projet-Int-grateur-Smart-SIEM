# app/tasks/notification_tasks.py
# -------------------------------
# Taches Celery pour les notifications et la purge
#
# ATTENTION : les workers Celery sont forké depuis le processus parent.
# L'engine asyncpg ne survit pas proprement au fork (pool de connexions corrompu).
# On utilise donc les sessions synchrones (psycopg2) pour toutes les operations
# PostgreSQL dans les taches Celery.

import asyncio
import ssl
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx
from sqlalchemy import delete

from app.core.config import settings
from app.core.database import sync_session_factory
from app.core.elasticsearch import get_es
from app.models.sql_models import AuditLog, Notification
from app.repositories.log_repo import LogRepository
from app.services.email_templating import render_alert_email
from app.tasks.celery import celery_app


# =============================================================================
# EMAIL
# =============================================================================


@celery_app.task(bind=True, max_retries=3, autoretry_for=(Exception,))
def send_email_notification(self, to: str, subject: str, alert_data: dict):
    """Envoie un email au format HTML via SMTP."""
    if not settings.SMTP_HOST:
        raise ValueError("SMTP non configure (SMTP_HOST manquant)")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to

    # Partie texte (fallback pour les clients email basiques)
    text_body = (
        f"{subject}\n"
        f"{'=' * len(subject)}\n"
        f"Severite : {alert_data.get('severity', 'N/A')}\n"
        f"Regle    : {alert_data.get('rule_name', 'N/A')}\n"
        f"IP       : {alert_data.get('source_ip', 'N/A')}\n"
        f"Hote     : {alert_data.get('host', 'N/A')}\n"
        f"Type     : {alert_data.get('event_type', 'N/A')}\n"
        f"MITRE    : {alert_data.get('mitre_tactic', 'N/A')} / "
        f"{alert_data.get('mitre_technique', 'N/A')}\n"
        f"\n{alert_data.get('description', '')}"
    )
    part_text = MIMEText(text_body, "plain", "utf-8")
    msg.attach(part_text)

    # Partie HTML (affichee par defaut dans la plupart des clients)
    try:
        html_body = render_alert_email(alert_data)
        part_html = MIMEText(html_body, "html", "utf-8")
        msg.attach(part_html)
    except Exception as e:
        print(f"[EMAIL] Impossible de generer le HTML, envoi en texte seul : {e}")

    # Contexte TLS standard pour compatibilité maximale
    tls_context = ssl.create_default_context()
    tls_context.check_hostname = False
    tls_context.verify_mode = ssl.CERT_NONE

    try:
        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT or 587,
            timeout=15,
        ) as server:
            server.set_debuglevel(0)
            if settings.SMTP_USER:
                server.starttls(context=tls_context)
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD or "")
            server.send_message(msg)
    except smtplib.SMTPServerDisconnected:
        print(
            f"[EMAIL] Connexion SMTP fermee par le serveur "
            f"({settings.SMTP_HOST}:{settings.SMTP_PORT}). "
            f"Nouvelle tentative apres delai."
        )
        raise
    except (smtplib.SMTPException, OSError) as e:
        print(
            f"[EMAIL] Erreur SMTP vers {settings.SMTP_HOST}:{settings.SMTP_PORT} : {e}"
        )
        raise


# =============================================================================
# SLACK
# =============================================================================


@celery_app.task(bind=True, max_retries=3, autoretry_for=(Exception,))
def send_slack_notification(self, channel: str, message: str):
    """Envoie une notification Slack via webhook."""
    if not settings.SLACK_WEBHOOK_URL:
        raise ValueError("Slack non configure (SLACK_WEBHOOK_URL manquant)")

    try:
        resp = httpx.post(
            settings.SLACK_WEBHOOK_URL,
            json={"channel": channel, "text": message, "username": "Smart SIEM"},
            timeout=10,
        )
        resp.raise_for_status()
    except httpx.HTTPError as e:
        print(f"[SLACK] Erreur d'envoi vers {channel} : {e}")
        raise


# =============================================================================
# NOTIFICATION IN-APP (PostgreSQL via session synchrone)
# =============================================================================


@celery_app.task
def send_in_app_notification(user_id: int, title: str, message: str):
    """
    Cree une notification en base de donnees.
    Utilise une session synchrone (psycopg2) pour eviter les conflits
    de connexion asyncpg dans les workers Celery forke.
    """
    with sync_session_factory() as db:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            channel="in_app",
        )
        db.add(notif)
        db.flush()
        db.refresh(notif)
        db.commit()

    print(
        f"[NOTIFICATION] Notification #{notif.id} creee pour l'utilisateur {user_id}"
    )


# =============================================================================
# PURGE (retention)
# =============================================================================


@celery_app.task
def purge_old_logs():
    """
    Purge les logs (Elasticsearch) et audits (PostgreSQL) selon la politique
    de retention.
    - Elasticsearch : asynchrone (client natif, pas de fork issue)
    - PostgreSQL   : synchrone (psycopg2, evite asyncpg + fork)
    """
    result = {}

    # --- Purge Elasticsearch ---
    async def _purge_es():
        es = await get_es()
        log_repo = LogRepository(es)
        return await log_repo.delete_older_than(settings.LOG_RETENTION_DAYS)

    deleted_logs = asyncio.run(_purge_es())
    result["logs_deleted"] = deleted_logs
    result["log_retention_days"] = settings.LOG_RETENTION_DAYS

    # --- Purge PostgreSQL (synchrone) ---
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.AUDIT_RETENTION_DAYS)

    with sync_session_factory() as session:
        stmt = delete(AuditLog).where(AuditLog.created_at < cutoff)
        result_proxy = session.execute(stmt)
        session.flush()
        session.commit()
        deleted_audits = result_proxy.rowcount

    result["audits_deleted"] = deleted_audits
    result["audit_retention_days"] = settings.AUDIT_RETENTION_DAYS

    print(
        f"[PURGE] Supprime : {deleted_logs} logs (ES), "
        f"{deleted_audits} audits (PG)"
    )
    return result

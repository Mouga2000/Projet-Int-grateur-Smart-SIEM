# app/tasks/notification_tasks.py
# -------------------------------
# Taches Celery pour les notifications et la purge

import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx

from app.core.config import settings
from app.core.database import async_session_factory
from app.core.elasticsearch import ElasticsearchClient
from app.repositories.audit_repo import AuditRepository
from app.repositories.log_repo import LogRepository
from app.repositories.notification_repo import NotificationRepository
from app.services.email_templating import render_alert_email
from app.tasks.celery import celery_app


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

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT or 587) as server:
        if settings.SMTP_USER:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD or "")
        server.send_message(msg)


@celery_app.task(bind=True, max_retries=3, autoretry_for=(Exception,))
def send_slack_notification(self, channel: str, message: str):
    """Envoie une notification Slack via webhook."""
    if not settings.SLACK_WEBHOOK_URL:
        raise ValueError("Slack non configure (SLACK_WEBHOOK_URL manquant)")

    httpx.post(
        settings.SLACK_WEBHOOK_URL,
        json={"channel": channel, "text": message, "username": "Smart SIEM"},
        timeout=10,
    )


@celery_app.task
def send_in_app_notification(user_id: int, title: str, message: str):
    """Cree une notification en base de donnees."""

    async def _create():
        async with async_session_factory() as db:
            repo = NotificationRepository(db)
            await repo.create(user_id, title, message, channel="in_app")
            await db.commit()

    asyncio.run(_create())


@celery_app.task
def purge_old_logs():
    """Purge les logs et audits selon la politique de retention."""

    async def _purge():
        result = {}

        es = ElasticsearchClient()
        log_repo = LogRepository(es)
        deleted_logs = await log_repo.delete_older_than(settings.LOG_RETENTION_DAYS)
        result["logs_deleted"] = deleted_logs
        result["log_retention_days"] = settings.LOG_RETENTION_DAYS

        async with async_session_factory() as session:
            audit_repo = AuditRepository(session)
            deleted_audits = await audit_repo.delete_older_than(
                settings.AUDIT_RETENTION_DAYS
            )
            await session.commit()
            result["audits_deleted"] = deleted_audits
            result["audit_retention_days"] = settings.AUDIT_RETENTION_DAYS

        return result

    return asyncio.run(_purge())

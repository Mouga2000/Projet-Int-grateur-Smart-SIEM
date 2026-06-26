# app/tasks/notification_tasks.py
# -------------------------------
# Tâches Celery pour les notifications et la purge

import asyncio

from app.core.config import settings
from app.core.database import async_session_factory
from app.core.elasticsearch import ElasticsearchClient
from app.repositories.audit_repo import AuditRepository
from app.repositories.log_repo import LogRepository
from app.tasks.celery import celery_app


@celery_app.task(bind=True, max_retries=3)
def send_email_notification(self, to: str, subject: str, body: str):
    """Envoie un email via SMTP."""
    raise NotImplementedError("SMTP non configuré")


@celery_app.task
def send_in_app_notification(user_id: int, title: str, message: str):
    """Crée une notification en base de données (affichage frontend)."""
    raise NotImplementedError("Notifications in-app non implémentées")


@celery_app.task
def purge_old_logs():
    """
    Purge les logs Elasticsearch et audits PostgreSQL
    selon la politique de rétention configurée.
    Exécuté quotidiennement par Celery Beat à 3h UTC.
    """

    async def _purge():
        result = {}

        # --- Purge des logs Elasticsearch ---
        es = ElasticsearchClient()
        log_repo = LogRepository(es)
        deleted_logs = await log_repo.delete_older_than(settings.LOG_RETENTION_DAYS)
        result["logs_deleted"] = deleted_logs
        result["log_retention_days"] = settings.LOG_RETENTION_DAYS

        # --- Purge des audits PostgreSQL ---
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

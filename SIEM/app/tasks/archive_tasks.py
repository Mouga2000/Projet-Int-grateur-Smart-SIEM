# app/tasks/archive_tasks.py
# -------------------------------
# Tâche Celery pour l'archivage automatique des logs

import asyncio
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.database import async_session_factory
from app.core.elasticsearch import get_es as get_es_client
from app.repositories.archive_repo import ArchiveRepository
from app.repositories.log_repo import LogRepository
from app.services.archiver import ArchiverService
from app.tasks.celery import celery_app


async def _auto_archive():
    """Crée une archive des logs de plus de ARCHIVE_AFTER_DAYS jours."""
    if not settings.ARCHIVE_ENABLED:
        return {"success": False, "reason": "disabled"}

    date_to = datetime.now(timezone.utc) - timedelta(days=settings.ARCHIVE_AFTER_DAYS)
    date_from = date_to - timedelta(days=30)

    async with async_session_factory() as db:
        es = await get_es_client()
        log_repo = LogRepository(es)
        archive_repo = ArchiveRepository(db)

        try:
            count = await log_repo.count(query={"range": {"timestamp": {"lte": date_to.isoformat()}}})
        except Exception:
            count = 0

        if count == 0:
            print(f"[ARCHIVE] Aucun log a archiver avant {date_to.date()}")
            return {"success": True, "archived": 0}

        print(f"[ARCHIVE] {count} logs a archiver du {date_from.date()} au {date_to.date()}...")
        try:
            archive = await ArchiverService.create_archive(
                log_repo, archive_repo, date_from, date_to, user_id=0
            )
            print(f"[ARCHIVE] Archive #{archive['id']} créée ({archive.get('log_count', 0)} logs)")
            return {"success": True, "archive_id": archive["id"], "log_count": archive.get("log_count", 0)}
        except ValueError as e:
            print(f"[ARCHIVE] Erreur : {e}")
            return {"success": False, "error": str(e)}


@celery_app.task
def auto_archive_logs():
    """
    Tâche Celery : archive automatiquement les logs de plus de N jours.
    Planifiée dans Celery Beat (1 fois/semaine).
    """
    return asyncio.run(_auto_archive())

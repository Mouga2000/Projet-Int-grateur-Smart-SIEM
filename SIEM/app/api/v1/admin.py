# app/api/v1/admin.py
# -------------------------------
# Endpoints administrateur — Purge des données (rétention)

from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_role
from app.core.config import settings
from app.core.database import get_db
from app.core.elasticsearch import get_es
from app.repositories.audit_repo import AuditRepository
from app.repositories.log_repo import LogRepository
from app.utils.tags import Role

router = APIRouter(prefix="/admin", tags=["Administration"])


@router.post("/purge/logs")
async def purge_logs(
    days: int = Query(default=settings.LOG_RETENTION_DAYS, ge=1, le=3650),
    current_user: dict = Depends(require_role([Role.ADMINISTRATEUR])),
    es: AsyncElasticsearch = Depends(get_es),
):
    """
    Purge les logs Elasticsearch plus vieux que N jours.
    Réservé aux administrateurs.
    """
    repo = LogRepository(es)
    deleted = await repo.delete_older_than(days)
    # Note: pas de AuditRepository ici car ES pourrait être indisponible
    return {
        "deleted": deleted,
        "retention_days": days,
        "message": f"{deleted} logs supprimés (>{days} jours)",
    }


@router.post("/purge/audit")
async def purge_audit(
    days: int = Query(default=settings.AUDIT_RETENTION_DAYS, ge=1, le=3650),
    current_user: dict = Depends(require_role([Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """
    Purge les logs d'audit PostgreSQL plus vieux que N jours.
    Réservé aux administrateurs.
    """
    repo = AuditRepository(db)
    deleted = await repo.delete_older_than(days)
    await repo.log_action({
        "user_id": current_user["id"], "username": current_user.get("username", ""),
        "action": "purge_audit", "result": "success",
        "resource_type": "audit_log", "resource_id": str(deleted),
        "details": {"retention_days": days, "deleted": deleted},
    })
    return {
        "deleted": deleted,
        "retention_days": days,
        "message": f"{deleted} audits supprimés (>{days} jours)",
    }


@router.get("/retention")
async def get_retention_config(
    current_user: dict = Depends(require_role([Role.ADMINISTRATEUR])),
):
    """Affiche la configuration de rétention actuelle."""
    return {
        "log_retention_days": settings.LOG_RETENTION_DAYS,
        "audit_retention_days": settings.AUDIT_RETENTION_DAYS,
        "next_purge": "Tous les jours à 3h (Celery Beat)",
    }

# app/api/v1/alerts.py
# -------------------------------
# Endpoints /api/v1/alerts -- Gestion des alertes

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_role
from app.core.database import get_db
from app.repositories.alert_repo import AlertRepository
from app.utils.tags import Role

router = APIRouter(prefix="/alerts", tags=["Alertes"])


@router.get("/")
async def list_alerts(
    severity: Optional[str] = Query(None, description="Filtrer par severite"),
    status: Optional[str] = Query(None, description="Filtrer par statut"),
    search: Optional[str] = Query(None, description="Recherche dans le titre et la description"),
    date_from: Optional[str] = Query(None, description="Date debut (ISO)"),
    date_to: Optional[str] = Query(None, description="Date fin (ISO)"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Liste les alertes avec filtres."""
    repo = AlertRepository(db)
    filters = {}
    if severity:
        filters["niveau"] = severity
    if status:
        filters["statut"] = status
    if search:
        filters["search"] = search
    if date_from:
        filters["date_from"] = date_from
    if date_to:
        filters["date_to"] = date_to
    return await repo.search(filters=filters, page=page, size=size)


@router.get("/stats")
async def get_alert_stats(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Statistiques sur les alertes (total, par severite, par statut)."""
    repo = AlertRepository(db)
    all_alerts = await repo.search(filters={}, page=1, size=10000)
    items = all_alerts["items"]

    by_severity = {"info": 0, "low": 0, "medium": 0, "high": 0, "critical": 0}
    by_status = {"ouverte": 0, "en_cours": 0, "resolue": 0, "classee": 0}

    for a in items:
        sev = a.get("severity", "info")
        if sev in by_severity:
            by_severity[sev] += 1
        st = a.get("status", "ouverte")
        if st in by_status:
            by_status[st] += 1

    return {
        "total": len(items),
        "by_severity": by_severity,
        "by_status": by_status,
    }


@router.get("/{alert_id}")
async def get_alert(
    alert_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Detail d'une alerte."""
    repo = AlertRepository(db)
    alert = await repo.get_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte non trouvee")
    return alert


@router.patch("/{alert_id}")
async def update_alert(
    alert_id: int,
    status: str = Query(..., pattern="^(ouverte|en_cours|resolue|classee)$"),
    current_user: dict = Depends(require_role([Role.ANALYSTE, Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """Met a jour le statut d'une alerte (acquittement, resolution)."""
    repo = AlertRepository(db)
    success = await repo.update(alert_id, {"statut": status})
    if not success:
        raise HTTPException(status_code=404, detail="Alerte non trouvee")
    return await repo.get_by_id(alert_id)

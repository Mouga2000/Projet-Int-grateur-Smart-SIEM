# app/api/v1/incidents.py
# -------------------------------
# Endpoints /api/v1/incidents -- Tableau de suivi des incidents

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_role
from app.core.database import get_db
from app.repositories.incident_repo import IncidentRepository
from app.utils.tags import Role

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("/")
async def list_incidents(
    statut: Optional[str] = Query(None, pattern="^(ouverte|en_cours|resolue|classee)$"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Liste les incidents avec filtre par statut et pagination."""
    repo = IncidentRepository(db)
    return await repo.list_incidents(statut=statut, page=page, size=size)


@router.post("/")
async def create_incident(
    alert_ids: list[int] = Query(default=[], description="IDs des alertes a inclure"),
    current_user: dict = Depends(require_role([Role.ANALYSTE, Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """Cree un incident de securite, optionnellement a partir d'alertes."""
    repo = IncidentRepository(db)
    incident = await repo.create(
        {"alert_ids": alert_ids, "created_by": current_user["id"]}
    )
    return incident


@router.get("/{incident_id}")
async def get_incident(
    incident_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Detail d'un incident avec sa timeline complete."""
    repo = IncidentRepository(db)
    inc = await repo.get_by_id(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident non trouve")
    return inc


@router.patch("/{incident_id}/status")
async def update_incident_status(
    incident_id: int,
    statut: str = Query(..., pattern="^(ouverte|en_cours|resolue|classee)$"),
    notes: Optional[str] = Query(None, description="Notes de resolution"),
    current_user: dict = Depends(require_role([Role.ANALYSTE, Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """
    Met a jour le statut d'un incident.
    Chaque changement est journalise dans la timeline.
    """
    repo = IncidentRepository(db)
    success = await repo.update_status(incident_id, statut, current_user["id"], notes)
    if not success:
        raise HTTPException(status_code=404, detail="Incident non trouve")
    return await repo.get_by_id(incident_id)


@router.post("/{incident_id}/alerts")
async def add_alert_to_incident(
    incident_id: int,
    alert_id: int = Query(..., description="ID de l'alerte a ajouter"),
    current_user: dict = Depends(require_role([Role.ANALYSTE, Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """Ajoute une alerte a un incident existant."""
    repo = IncidentRepository(db)
    success = await repo.add_alert(incident_id, alert_id, current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Incident non trouve")
    return await repo.get_by_id(incident_id)


@router.post("/{incident_id}/assign")
async def assign_incident(
    incident_id: int,
    user_id: int = Query(..., description="ID de l'utilisateur a assigner"),
    current_user: dict = Depends(require_role([Role.ANALYSTE, Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """Assigne un incident a un analyste."""
    repo = IncidentRepository(db)
    success = await repo.assign(incident_id, user_id, current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Incident non trouve")
    return await repo.get_by_id(incident_id)

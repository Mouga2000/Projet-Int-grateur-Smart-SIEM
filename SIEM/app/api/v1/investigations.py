# app/api/v1/investigations.py
# -------------------------------
# Endpoints pour le marquage d'evenements suspects et investigation croisee

from typing import List, Optional

from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_role
from app.core.database import get_db
from app.core.elasticsearch import get_es
from app.repositories.audit_repo import AuditRepository
from app.repositories.investigation_repo import InvestigationRepository
from app.utils.tags import Role

router = APIRouter(prefix="/investigations", tags=["Investigations"])


# --- Schemas ---


class AddLogRequest(BaseModel):
    log_id: str = Field(..., description="ID Elasticsearch du log a marquer")
    note: Optional[str] = Field(None, description="Note d'analyse de l'analyste")
    verdict: str = Field(
        default="suspect",
        description="Verdict : suspect, benign, confirmed, false_positive",
    )


class CreateInvestigationRequest(BaseModel):
    title: str = Field(
        ..., min_length=3, max_length=255, description="Titre de l'investigation"
    )
    description: Optional[str] = Field(None, description="Description detaillee")
    severity: str = Field(default="medium", description="low, medium, high, critical")
    tags: List[str] = Field(default=[], description="Tags personnalises")
    log_ids: List[str] = Field(default=[], description="IDs des logs a inclure")
    mitre_tactic: Optional[str] = Field(None, description="Tactique MITRE ATT&CK")
    mitre_technique: Optional[str] = Field(None, description="Technique MITRE ATT&CK")


class UpdateInvestigationRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    severity: Optional[str] = None
    tags: Optional[List[str]] = None
    assigned_to: Optional[int] = None
    mitre_tactic: Optional[str] = None
    mitre_technique: Optional[str] = None


# --- Endpoints ---


@router.post("/")
async def create_investigation(
    data: CreateInvestigationRequest,
    current_user: dict = Depends(require_role([Role.ANALYSTE, Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """Cree une nouvelle investigation pour regrouper des logs suspects."""
    repo = InvestigationRepository(db)
    inv = await repo.create({**data.model_dump(), "created_by": current_user["id"]})
    audit = AuditRepository(db)
    await audit.log_action({
        "user_id": current_user["id"], "username": current_user.get("username", ""),
        "action": "create_investigation", "result": "success",
        "resource_type": "investigation", "resource_id": str(inv.get("id", "")),
        "details": {"title": data.title, "severity": data.severity},
    })
    return inv


@router.get("/")
async def list_investigations(
    status: Optional[str] = Query(None, pattern="^(ouverte|en_cours|resolue|classee)$"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Liste toutes les investigations avec filtre par statut."""
    repo = InvestigationRepository(db)
    items = await repo.list_investigations(
        status=status, limit=size, offset=(page - 1) * size
    )
    total = await repo.count(status=status)
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": max(1, (total + size - 1) // size),
    }


@router.get("/{investigation_id}")
async def get_investigation(
    investigation_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Detail d'une investigation avec ses logs associes."""
    repo = InvestigationRepository(db)
    inv = await repo.get_by_id(investigation_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation non trouvee")

    logs = await repo.get_logs_for_investigation(investigation_id)
    inv["logs"] = logs
    return inv


@router.post("/{investigation_id}/logs")
async def add_log_to_investigation(
    investigation_id: int,
    data: AddLogRequest,
    current_user: dict = Depends(require_role([Role.ANALYSTE, Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
    es: AsyncElasticsearch = Depends(get_es),
):
    """
    Ajoute un log a une investigation avec une note d'analyse.

    Permet de marquer un evenement comme suspect et de le lier
    a d'autres logs pour une enquete croisee.
    """
    # Verifier que le log existe dans Elasticsearch
    try:
        from app.core.config import settings
        log_doc = await es.get(index=settings.ELASTICSEARCH_INDEX_LOGS, id=data.log_id)
    except Exception:
        raise HTTPException(
            status_code=404,
            detail="Log non trouve dans Elasticsearch",
        )

    repo = InvestigationRepository(db)
    result = await repo.add_log(
        investigation_id=investigation_id,
        log_id=data.log_id,
        note=data.note,
        verdict=data.verdict,
        user_id=current_user["id"],
    )

    result["log"] = {
        "id": log_doc["_id"],
        "timestamp": log_doc["_source"].get("timestamp"),
        "source_ip": log_doc["_source"].get("source_ip"),
        "host": log_doc["_source"].get("host"),
        "severity": log_doc["_source"].get("severity"),
        "raw_message": log_doc["_source"].get("raw_message", "")[:200],
    }

    return result


@router.patch("/{investigation_id}/status")
async def update_investigation_status(
    investigation_id: int,
    status: str = Query(..., pattern="^(ouverte|en_cours|resolue|classee)$"),
    notes: Optional[str] = Query(None),
    current_user: dict = Depends(require_role([Role.ANALYSTE, Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """Met a jour le statut d'une investigation."""
    repo = InvestigationRepository(db)
    success = await repo.update_status(investigation_id, status, notes)
    if not success:
        raise HTTPException(status_code=404, detail="Investigation non trouvee")
    audit = AuditRepository(db)
    await audit.log_action({
        "user_id": current_user["id"], "username": current_user.get("username", ""),
        "action": f"investigation_{status}", "result": "success",
        "resource_type": "investigation", "resource_id": str(investigation_id),
        "details": {"notes": notes} if notes else {},
    })
    return {"message": f"Statut mis a jour : {status}"}


@router.patch("/{investigation_id}")
async def update_investigation(
    investigation_id: int,
    data: UpdateInvestigationRequest,
    current_user: dict = Depends(require_role([Role.ANALYSTE, Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """Modifie une investigation (titre, description, severite, tags, assignation)."""
    repo = InvestigationRepository(db)
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Aucune donnee a mettre a jour")
    success = await repo.update(investigation_id, update_data)
    if not success:
        raise HTTPException(status_code=404, detail="Investigation non trouvee")
    return await repo.get_by_id(investigation_id)

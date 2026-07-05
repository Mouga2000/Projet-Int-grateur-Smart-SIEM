# app/api/v1/playbooks.py
# -------------------------------
# Endpoints /api/v1/playbooks -- Playbooks SOAR (automatisation)

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_role
from app.core.database import get_db
from app.repositories.audit_repo import AuditRepository
from app.repositories.playbook_repo import PlaybookRepository
from app.services.soar import SOARService
from app.utils.tags import Role

router = APIRouter(prefix="/playbooks", tags=["Playbooks SOAR"])


# --- Schemas ---


class PlaybookCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    trigger: str = Field(
        default="manual", pattern="^(manual|alert_created|scheduled|webhook)$"
    )
    steps: list = []
    variables: dict = {}
    timeout_seconds: int = 300
    max_retries: int = 3


class PlaybookUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    trigger: Optional[str] = None
    steps: Optional[list] = None
    variables: Optional[dict] = None
    timeout_seconds: Optional[int] = None
    max_retries: Optional[int] = None


# --- Endpoints ---


@router.get("/")
async def list_playbooks(
    trigger: Optional[str] = Query(None, description="Filtrer par declencheur"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Liste les playbooks disponibles."""
    repo = PlaybookRepository(db)
    if trigger:
        return await repo.get_by_trigger(trigger)
    return await repo.get_enabled_playbooks()


@router.post("/", status_code=201)
async def create_playbook(
    data: PlaybookCreate,
    current_user: dict = Depends(require_role([Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """Cree un nouveau playbook."""
    repo = PlaybookRepository(db)
    pb = await repo.create({**data.dict(), "created_by": current_user["username"]})
    audit = AuditRepository(db)
    await audit.log_action({
        "user_id": current_user["id"], "username": current_user.get("username", ""),
        "action": "create_playbook", "result": "success",
        "resource_type": "playbook", "resource_id": str(pb.get("id", "")),
        "details": {"name": data.name, "trigger": data.trigger},
    })
    return pb


@router.get("/{playbook_id}")
async def get_playbook(
    playbook_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Detail d'un playbook."""
    repo = PlaybookRepository(db)
    pb = await repo.get_by_id(playbook_id)
    if not pb:
        raise HTTPException(status_code=404, detail="Playbook non trouve")
    return pb


@router.put("/{playbook_id}")
async def update_playbook(
    playbook_id: int,
    data: PlaybookUpdate,
    current_user: dict = Depends(require_role([Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """Modifie un playbook."""
    repo = PlaybookRepository(db)
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Aucune donnee a mettre a jour")
    success = await repo.update(playbook_id, update_data)
    if not success:
        raise HTTPException(status_code=404, detail="Playbook non trouve")
    pb = await repo.get_by_id(playbook_id)
    audit = AuditRepository(db)
    await audit.log_action({
        "user_id": current_user["id"], "username": current_user.get("username", ""),
        "action": "update_playbook", "result": "success",
        "resource_type": "playbook", "resource_id": str(playbook_id),
        "details": {"changes": list(update_data.keys())},
    })
    return pb


@router.delete("/{playbook_id}", status_code=204)
async def delete_playbook(
    playbook_id: int,
    current_user: dict = Depends(require_role([Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """Supprime (soft-delete) un playbook."""
    repo = PlaybookRepository(db)
    success = await repo.delete(playbook_id)
    if not success:
        raise HTTPException(status_code=404, detail="Playbook non trouve")
    audit = AuditRepository(db)
    await audit.log_action({
        "user_id": current_user["id"], "username": current_user.get("username", ""),
        "action": "delete_playbook", "result": "success",
        "resource_type": "playbook", "resource_id": str(playbook_id),
    })


@router.post("/{playbook_id}/execute")
async def execute_playbook(
    playbook_id: int,
    context: dict = {},
    current_user: dict = Depends(require_role([Role.ANALYSTE, Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute un playbook manuellement.

    Contexte attendu (selon les actions du playbook) :
    {
        "source_ip": "192.168.1.100",
        "host": "192.168.1.50",
        "user": "admin"
    }
    """
    repo = PlaybookRepository(db)
    soar = SOARService(repo)
    result = await soar.execute_playbook(playbook_id, context)
    audit = AuditRepository(db)
    await audit.log_action({
        "user_id": current_user["id"], "username": current_user.get("username", ""),
        "action": "execute_playbook", "result": "success" if result.get("success") else "failed",
        "resource_type": "playbook", "resource_id": str(playbook_id),
        "details": {"target_ip": context.get("source_ip", ""), "success": result.get("success")},
    })
    return result

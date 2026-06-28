# app/api/v1/rules.py
# -------------------------------
# Endpoints /api/v1/rules -- Gestion des regles de correlation

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_role
from app.core.database import get_db
from app.repositories.rule_repo import RuleRepository
from app.utils.tags import Role

router = APIRouter(prefix="/rules", tags=["Regles de correlation"])


# --- Schemas ---


class RuleCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    rule_type: str = Field(
        default="single_event",
        pattern="^(single_event|threshold|sequence|correlation|ueba|custom)$",
    )
    severity: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    priority: int = Field(default=50, ge=0, le=100)
    condition: dict = {}
    actions: dict = {}
    mitre_tactic: Optional[str] = None
    mitre_technique: Optional[str] = None
    enabled: bool = True


class RuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    priority: Optional[int] = None
    condition: Optional[dict] = None
    actions: Optional[dict] = None
    mitre_tactic: Optional[str] = None
    mitre_technique: Optional[str] = None
    enabled: Optional[bool] = None


# --- Endpoints ---


@router.get("/")
async def list_rules(
    rule_type: Optional[str] = Query(None, description="Filtrer par type de regle"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Liste toutes les regles de correlation."""
    repo = RuleRepository(db)
    if rule_type:
        return await repo.get_by_type(rule_type)
    return await repo.get_enabled_rules()


@router.post("/")
async def create_rule(
    data: RuleCreate,
    current_user: dict = Depends(require_role([Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """Cree une nouvelle regle de correlation."""
    repo = RuleRepository(db)
    rule = await repo.create({**data.dict(), "created_by": current_user["username"]})
    return rule


@router.get("/{rule_id}")
async def get_rule(
    rule_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Detail d'une regle."""
    repo = RuleRepository(db)
    rule = await repo.get_by_id(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Regle non trouvee")
    return rule


@router.patch("/{rule_id}")
async def update_rule(
    rule_id: int,
    data: RuleUpdate,
    current_user: dict = Depends(require_role([Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """Modifie une regle."""
    repo = RuleRepository(db)
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Aucune donnee a mettre a jour")
    success = await repo.update(rule_id, update_data)
    if not success:
        raise HTTPException(status_code=404, detail="Regle non trouvee")
    return await repo.get_by_id(rule_id)


@router.delete("/{rule_id}")
async def delete_rule(
    rule_id: int,
    current_user: dict = Depends(require_role([Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """Supprime (soft-delete) une regle."""
    repo = RuleRepository(db)
    success = await repo.delete(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Regle non trouvee")
    return {"message": "Regle supprimee"}

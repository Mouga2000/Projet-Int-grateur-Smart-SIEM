# app/api/v1/ueba.py
# -------------------------------
# Endpoints /api/v1/ueba — Profilage comportemental UEBA

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_role
from app.core.database import get_db
from app.models.sql_models import ProfilUEBA
from app.services import ueba as ueba_service
from app.utils.tags import Role

router = APIRouter(prefix="/ueba", tags=["UEBA"])


@router.get("/profile/{entity_id}")
async def get_ueba_profile(
    entity_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retourne le profil UEBA d'une entité (utilisateur ou hôte).

    Affiche le score de risque, la baseline comportementale
    et la dernière mise à jour.
    """
    profile = await ueba_service.get_profile(db, entity_id)
    if not profile:
        return {
            "entity_id": entity_id,
            "risk_score": 0,
            "baseline": {},
            "message": "Aucun profil UEBA trouvé pour cette entité",
        }
    return profile


@router.get("/scores")
async def list_ueba_scores(
    min_score: int = Query(0, ge=0, le=100, description="Score minimum"),
    limit: int = Query(50, ge=1, le=500, description="Nombre max de résultats"),
    current_user: dict = Depends(require_role([Role.ANALYSTE, Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """
    Liste les scores de risque UEBA, du plus élevé au plus bas.

    Utile pour identifier les entités les plus suspectes.
    """
    result = await db.execute(
        select(ProfilUEBA)
        .where(ProfilUEBA.risk_score >= min_score)
        .order_by(desc(ProfilUEBA.risk_score))
        .limit(limit)
    )

    profiles = []
    for p in result.scalars().all():
        profiles.append({
            "id": p.id,
            "entity_id": p.entity_id,
            "entity_type": p.entity_type,
            "risk_score": p.risk_score,
            "last_updated": p.last_updated.isoformat() if p.last_updated else None,
        })

    return {
        "items": profiles,
        "total": len(profiles),
        "min_score": min_score,
    }

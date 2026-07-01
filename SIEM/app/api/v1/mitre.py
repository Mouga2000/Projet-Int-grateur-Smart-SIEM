# app/api/v1/mitre.py
# -------------------------------
# Endpoints /api/v1/mitre -- Referentiel MITRE ATT&CK

from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_current_user
from app.utils.mitre import (
    get_all_techniques,
    get_mitre_technique,
    get_tactics,
    get_techniques_by_tactic,
)

router = APIRouter(prefix="/mitre", tags=["MITRE ATT&CK"])


@router.get("/tactics")
async def list_tactics():
    """Liste toutes les tactiques MITRE ATT&CK."""
    return {"tactics": get_tactics(), "count": len(get_tactics())}


@router.get("/techniques")
async def list_techniques(
    tactic: Optional[str] = Query(None, description="Filtrer par tactique"),
    current_user: dict = Depends(get_current_user),
):
    """
    Liste les techniques MITRE ATT&CK.
    Option : filtrer par tactique (?tactic=lateral_movement)
    """
    if tactic:
        techniques = get_techniques_by_tactic(tactic)
        return {
            "tactic": tactic,
            "techniques": techniques,
            "count": len(techniques),
        }
    all_techs = get_all_techniques()
    return {"techniques": all_techs, "count": len(all_techs)}


@router.get("/techniques/{technique_id}")
async def get_technique(
    technique_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Detail d'une technique MITRE ATT&CK par son ID (ex: T1110)."""
    technique = get_mitre_technique(technique_id.upper())
    if not technique:
        return {"error": f"Technique {technique_id} non trouvee"}, 404
    return {"id": technique_id.upper(), **technique}

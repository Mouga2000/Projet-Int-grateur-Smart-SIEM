# app/api/v1/audit.py
# -------------------------------
# Endpoints /api/v1/audit — Logs d'audit PostgreSQL

import csv
import io
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_role
from app.core.database import get_db
from app.repositories.audit_repo import AuditRepository
from app.utils.tags import Role

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/logs")
async def get_audit_logs(
    username: Optional[str] = Query(None, description="Filtrer par nom d'utilisateur"),
    user_id: Optional[str] = Query(None, description="Filtrer par ID utilisateur"),
    action: Optional[str] = Query(None, description="Filtrer par action"),
    resource_type: Optional[str] = Query(None, description="Filtrer par type de ressource"),
    date_from: Optional[str] = Query(None, description="Date debut (ISO)"),
    date_to: Optional[str] = Query(None, description="Date fin (ISO)"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(require_role([Role.AUDITEUR, Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """Retourne les logs d'audit (traces des actions utilisateurs)."""
    repo = AuditRepository(db)

    filters = {}
    if username:
        filters["username"] = username
    if user_id:
        filters["user_id"] = int(user_id)
    if action:
        filters["action"] = action
    if resource_type:
        filters["resource_type"] = resource_type

    if date_from:
        filters["date_from"] = date_from
    if date_to:
        filters["date_to"] = date_to

    offset = (page - 1) * size
    items = await repo.get_audit_logs(filters=filters or None, limit=size, offset=offset)
    total = await repo.count(filters=filters or None)

    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
    }


@router.get("/logs/export")
async def export_audit_logs(
    date_from: Optional[str] = Query(None, description="Date debut (ISO)"),
    date_to: Optional[str] = Query(None, description="Date fin (ISO)"),
    current_user: dict = Depends(require_role([Role.AUDITEUR, Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """Exporte les logs d'audit au format CSV."""
    repo = AuditRepository(db)

    filters = {}
    items = await repo.get_audit_logs(filters=filters or None, limit=5000, offset=0)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Utilisateur", "Action", "Resultat", "Ressource", "ID Ressource", "IP", "Details"])

    for item in items:
        writer.writerow([
            item.get("timestamp", ""),
            item.get("username", ""),
            item.get("action", ""),
            item.get("result", ""),
            item.get("resource_type", ""),
            item.get("resource_id", ""),
            item.get("ip_address", ""),
            str(item.get("details", {})),
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit-logs.csv"},
    )

# app/repositories/investigation_repo.py
# -------------------------------
# Repository pour Investigation + InvestigationLog — PostgreSQL

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sql_models import Investigation, InvestigationLog


class InvestigationRepository:
    """CRUD pour les investigations et leurs logs associes."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ----------------------------------------------------------------
    # Investigations
    # ----------------------------------------------------------------

    async def create(self, data: dict) -> dict:
        inv = Investigation(
            title=data["title"],
            description=data.get("description"),
            severity=data.get("severity", "medium"),
            tags=data.get("tags", []),
            log_ids=data.get("log_ids", []),
            mitre_tactic=data.get("mitre_tactic"),
            mitre_technique=data.get("mitre_technique"),
            created_by=data.get("created_by"),
        )
        self.db.add(inv)
        await self.db.flush()
        await self.db.refresh(inv)
        return self._to_dict(inv)

    async def get_by_id(self, investigation_id: int) -> Optional[dict]:
        result = await self.db.execute(
            select(Investigation).where(Investigation.id == investigation_id)
        )
        inv = result.scalar_one_or_none()
        return self._to_dict(inv) if inv else None

    async def list_investigations(
        self, status: str = None, limit: int = 100, offset: int = 0
    ) -> List[dict]:
        stmt = select(Investigation).order_by(Investigation.id.desc())
        if status:
            stmt = stmt.where(Investigation.status == status)
        result = await self.db.execute(stmt.offset(offset).limit(limit))
        return [self._to_dict(i) for i in result.scalars().all()]

    async def update(self, inv_id: int, data: dict) -> bool:
        result = await self.db.execute(
            select(Investigation).where(Investigation.id == inv_id)
        )
        inv = result.scalar_one_or_none()
        if not inv:
            return False
        for key in [
            "title",
            "description",
            "severity",
            "tags",
            "assigned_to",
            "mitre_tactic",
            "mitre_technique",
        ]:
            if key in data:
                setattr(inv, key, data[key])
        await self.db.flush()
        return True

    async def update_status(self, inv_id: int, status: str, notes: str = None) -> bool:
        result = await self.db.execute(
            select(Investigation).where(Investigation.id == inv_id)
        )
        inv = result.scalar_one_or_none()
        if not inv:
            return False
        inv.status = status
        if notes:
            inv.resolution_notes = notes
        if status in ("resolue", "classee"):
            inv.closed_at = datetime.now(timezone.utc)
        await self.db.flush()
        return True

    async def count(self, status: str = None) -> int:
        stmt = select(Investigation)
        if status:
            stmt = stmt.where(Investigation.status == status)
        result = await self.db.execute(stmt)
        return len(result.scalars().all())

    # ----------------------------------------------------------------
    # Logs lies a une investigation
    # ----------------------------------------------------------------

    async def add_log(
        self,
        investigation_id: int,
        log_id: str,
        note: str = None,
        verdict: str = "suspect",
        user_id: int = None,
    ) -> dict:
        # Creer le lien
        link = InvestigationLog(
            investigation_id=investigation_id,
            log_id=log_id,
            analyst_note=note,
            analyst_verdict=verdict,
            added_by=user_id,
        )
        self.db.add(link)

        # Mettre a jour la liste log_ids dans l'investigation
        inv_result = await self.db.execute(
            select(Investigation).where(Investigation.id == investigation_id)
        )
        inv = inv_result.scalar_one_or_none()
        if inv and log_id not in (inv.log_ids or []):
            inv.log_ids = (inv.log_ids or []) + [log_id]

        await self.db.flush()
        await self.db.refresh(link)
        return {
            "id": link.id,
            "investigation_id": link.investigation_id,
            "log_id": link.log_id,
            "note": link.analyst_note,
            "verdict": link.analyst_verdict,
            "added_by": link.added_by,
            "created_at": link.created_at.isoformat() if link.created_at else None,
        }

    async def get_logs_for_investigation(self, investigation_id: int) -> List[dict]:
        result = await self.db.execute(
            select(InvestigationLog)
            .where(InvestigationLog.investigation_id == investigation_id)
            .order_by(InvestigationLog.id.desc())
        )
        return [
            {
                "id": link.id,
                "log_id": link.log_id,
                "log_index": link.log_index,
                "note": link.analyst_note,
                "verdict": link.analyst_verdict,
                "added_by": link.added_by,
                "created_at": link.created_at.isoformat() if link.created_at else None,
            }
            for link in result.scalars().all()
        ]

    # ----------------------------------------------------------------
    # Helper
    # ----------------------------------------------------------------

    @staticmethod
    def _to_dict(inv: Investigation) -> dict:
        return {
            "id": inv.id,
            "title": inv.title,
            "description": inv.description,
            "status": inv.status,
            "severity": inv.severity,
            "tags": inv.tags or [],
            "log_ids": inv.log_ids or [],
            "mitre_tactic": inv.mitre_tactic,
            "mitre_technique": inv.mitre_technique,
            "created_by": inv.created_by,
            "assigned_to": inv.assigned_to,
            "closed_at": inv.closed_at.isoformat() if inv.closed_at else None,
            "resolution_notes": inv.resolution_notes,
            "created_at": inv.created_at.isoformat() if inv.created_at else None,
            "updated_at": inv.updated_at.isoformat() if inv.updated_at else None,
        }

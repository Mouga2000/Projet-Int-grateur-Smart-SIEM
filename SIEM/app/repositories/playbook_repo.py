# app/repositories/playbook_repo.py
# -------------------------------
# Repository pour Playbook — PostgreSQL

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sql_models import Playbook


class PlaybookRepository:
    """CRUD pour les playbooks SOAR."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> dict:
        pb = Playbook(
            name=data["name"],
            description=data.get("description"),
            trigger=data.get("trigger", "manual"),
            enabled=data.get("enabled", True),
            steps=data.get("steps", []),
            variables=data.get("variables", {}),
            timeout_seconds=data.get("timeout_seconds", 300),
            max_retries=data.get("max_retries", 3),
            created_by=data.get("created_by"),
        )
        self.db.add(pb)
        await self.db.flush()
        await self.db.refresh(pb)
        return self._to_dict(pb)

    async def get_by_id(self, playbook_id: int) -> Optional[dict]:
        result = await self.db.execute(
            select(Playbook).where(Playbook.id == playbook_id)
        )
        pb = result.scalar_one_or_none()
        return self._to_dict(pb) if pb else None

    async def get_enabled_playbooks(self) -> List[dict]:
        result = await self.db.execute(
            select(Playbook).where(
                Playbook.enabled == True, Playbook.deleted_at.is_(None)
            )
        )
        return [self._to_dict(pb) for pb in result.scalars().all()]

    async def get_by_trigger(self, trigger: str) -> List[dict]:
        """Playbooks declenches automatiquement (ex: alert_created, scheduled)."""
        result = await self.db.execute(
            select(Playbook).where(
                Playbook.trigger == trigger,
                Playbook.enabled == True,
                Playbook.deleted_at.is_(None),
            )
        )
        return [self._to_dict(pb) for pb in result.scalars().all()]

    async def update(self, playbook_id: int, data: dict) -> bool:
        result = await self.db.execute(
            select(Playbook).where(Playbook.id == playbook_id)
        )
        pb = result.scalar_one_or_none()
        if not pb:
            return False
        for key in [
            "name",
            "description",
            "enabled",
            "trigger",
            "steps",
            "variables",
            "timeout_seconds",
            "max_retries",
        ]:
            if key in data:
                setattr(pb, key, data[key])
        await self.db.flush()
        return True

    async def increment_execution(self, playbook_id: int) -> bool:
        result = await self.db.execute(
            select(Playbook).where(Playbook.id == playbook_id)
        )
        pb = result.scalar_one_or_none()
        if not pb:
            return False
        pb.execution_count = (pb.execution_count or 0) + 1
        pb.last_executed_at = datetime.now(timezone.utc)
        await self.db.flush()
        return True

    async def delete(self, playbook_id: int) -> bool:
        result = await self.db.execute(
            select(Playbook).where(Playbook.id == playbook_id)
        )
        pb = result.scalar_one_or_none()
        if not pb:
            return False
        pb.deleted_at = datetime.now(timezone.utc)
        await self.db.flush()
        return True

    @staticmethod
    def _to_dict(pb: Playbook) -> dict:
        return {
            "id": pb.id,
            "name": pb.name,
            "description": pb.description,
            "trigger": pb.trigger,
            "enabled": pb.enabled,
            "steps": pb.steps or [],
            "variables": pb.variables or {},
            "timeout_seconds": pb.timeout_seconds,
            "max_retries": pb.max_retries,
            "execution_count": pb.execution_count,
            "last_executed_at": pb.last_executed_at.isoformat()
            if pb.last_executed_at
            else None,
            "created_by": pb.created_by,
            "created_at": pb.created_at.isoformat() if pb.created_at else None,
            "updated_at": pb.updated_at.isoformat() if pb.updated_at else None,
        }

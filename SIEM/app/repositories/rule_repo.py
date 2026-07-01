# app/repositories/rule_repo.py
# -------------------------------
# Repository pour Rule — PostgreSQL (SQLAlchemy)

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sql_models import Rule


class RuleRepository:
    """CRUD pour les regles de correlation dans PostgreSQL."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> dict:
        rule = Rule(
            name=data["name"],
            description=data.get("description"),
            rule_type=data.get("rule_type", "single_event"),
            enabled=data.get("enabled", True),
            severity=data.get("severity", "medium"),
            condition=data.get("condition", {}),
            actions=data.get("actions", {}),
            mitre_tactic=data.get("mitre_tactic"),
            mitre_technique=data.get("mitre_technique"),
            priority=data.get("priority", 50),
            created_by=data.get("created_by"),
        )
        self.db.add(rule)
        await self.db.flush()
        await self.db.refresh(rule)
        return self._to_dict(rule)

    async def get_enabled_rules(self) -> List[dict]:
        """Recupere toutes les regles actives, triees par priorite."""
        result = await self.db.execute(
            select(Rule)
            .where(Rule.enabled == True, Rule.deleted_at.is_(None))
            .order_by(Rule.priority.desc())
        )
        return [self._to_dict(r) for r in result.scalars().all()]

    async def get_by_id(self, rule_id: int) -> Optional[dict]:
        result = await self.db.execute(select(Rule).where(Rule.id == rule_id))
        rule = result.scalar_one_or_none()
        return self._to_dict(rule) if rule else None

    async def get_by_type(self, rule_type: str) -> List[dict]:
        result = await self.db.execute(
            select(Rule).where(Rule.rule_type == rule_type, Rule.enabled == True)
        )
        return [self._to_dict(r) for r in result.scalars().all()]

    async def update(self, rule_id: int, data: dict) -> bool:
        result = await self.db.execute(select(Rule).where(Rule.id == rule_id))
        rule = result.scalar_one_or_none()
        if not rule:
            return False
        for key in [
            "name",
            "description",
            "enabled",
            "severity",
            "condition",
            "actions",
            "priority",
            "mitre_tactic",
            "mitre_technique",
        ]:
            if key in data:
                setattr(rule, key, data[key])
        await self.db.flush()
        return True

    async def delete(self, rule_id: int) -> bool:
        result = await self.db.execute(select(Rule).where(Rule.id == rule_id))
        rule = result.scalar_one_or_none()
        if not rule:
            return False
        rule.deleted_at = datetime.now(timezone.utc)
        await self.db.flush()
        return True

    @staticmethod
    def _to_dict(rule: Rule) -> dict:
        return {
            "id": rule.id,
            "name": rule.name,
            "description": rule.description,
            "type": rule.rule_type,
            "enabled": rule.enabled,
            "severity": rule.severity,
            "priority": rule.priority,
            "condition": rule.condition or {},
            "actions": rule.actions or {},
            "mitre_tactic": rule.mitre_tactic,
            "mitre_technique": rule.mitre_technique,
            "version": rule.version,
            "created_by": rule.created_by,
            "created_at": rule.created_at.isoformat() if rule.created_at else None,
        }

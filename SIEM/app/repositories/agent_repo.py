# app/repositories/agent_repo.py
# -------------------------------
# Repository pour les agents SOAR

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sql_models import Agent


class AgentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, hostname: str, ip_address: str,
                       agent_port: int = 9000,
                       operating_system: Optional[str] = None) -> dict:
        """Enregistre ou met à jour un agent (upsert sur hostname)."""
        result = await self.db.execute(
            select(Agent).where(Agent.hostname == hostname)
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.ip_address = ip_address
            existing.agent_port = agent_port
            if operating_system:
                existing.operating_system = operating_system
            existing.is_active = True
            existing.last_seen = datetime.now(timezone.utc)
            await self.db.flush()
            await self.db.refresh(existing)
            return self._to_dict(existing)
        else:
            agent = Agent(
                hostname=hostname,
                ip_address=ip_address,
                agent_port=agent_port,
                operating_system=operating_system,
                is_active=True,
                last_seen=datetime.now(timezone.utc),
            )
            self.db.add(agent)
            await self.db.flush()
            await self.db.refresh(agent)
            return self._to_dict(agent)

    async def list_active(self) -> List[dict]:
        """Retourne la liste des agents actifs."""
        result = await self.db.execute(
            select(Agent).where(Agent.is_active == True).order_by(Agent.hostname)
        )
        return [self._to_dict(a) for a in result.scalars().all()]

    @staticmethod
    def _to_dict(agent: Agent) -> dict:
        return {
            "id": agent.id,
            "hostname": agent.hostname,
            "ip_address": agent.ip_address,
            "agent_port": agent.agent_port,
            "operating_system": agent.operating_system,
            "last_seen": agent.last_seen.isoformat() if agent.last_seen else None,
        }

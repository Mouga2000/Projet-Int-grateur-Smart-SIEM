# app/repositories/alert_repo.py
# -------------------------------
# Repository pour Alert — table PostgreSQL "alertes"

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sql_models import Alert


class AlertRepository:
    """CRUD pour les alertes dans PostgreSQL."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, alert_data: dict) -> int:
        alert = Alert(
            regle_id=alert_data.get("rule_id"),
            titre=alert_data.get("rule_name", "Alerte"),
            description=alert_data.get("description"),
            niveau=alert_data.get("severity", "medium"),
            source_ip=alert_data.get("source_ip"),
            host=alert_data.get("host"),
            mitre=alert_data.get("mitre", {}),
            statut="ouverte",
            score_confiance=alert_data.get("score", 50),
        )
        self.db.add(alert)
        await self.db.flush()
        await self.db.refresh(alert)
        return alert.id

    async def get_by_id(self, alert_id: int) -> Optional[dict]:
        result = await self.db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()
        return self._to_dict(alert) if alert else None

    async def search(self, filters: dict = None, page: int = 1, size: int = 50) -> dict:
        stmt = select(Alert).order_by(desc(Alert.cree_le))
        if filters:
            if filters.get("niveau"):
                stmt = stmt.where(Alert.niveau == filters["niveau"])
            if filters.get("statut"):
                stmt = stmt.where(Alert.statut == filters["statut"])
        result = await self.db.execute(stmt.offset((page - 1) * size).limit(size))
        items = [self._to_dict(a) for a in result.scalars().all()]
        return {"items": items, "total": len(items), "page": page, "size": size}

    async def update(self, alert_id: int, update_data: dict) -> bool:
        result = await self.db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()
        if not alert:
            return False
        for key in ["statut", "score_confiance"]:
            if key in update_data:
                setattr(alert, key, update_data[key])
        await self.db.flush()
        return True

    @staticmethod
    def _to_dict(alert: Alert) -> dict:
        return {
            "id": alert.id,
            "rule_id": alert.regle_id,
            "title": alert.titre,
            "description": alert.description,
            "severity": alert.niveau,
            "source_ip": alert.source_ip,
            "host": alert.host,
            "status": alert.statut,
            "confidence": alert.score_confiance,
            "mitre": alert.mitre or {},
            "created_at": alert.cree_le.isoformat() if alert.cree_le else None,
        }

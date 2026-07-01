# app/repositories/incident_repo.py
# -------------------------------
# Repository pour Incident — PostgreSQL

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sql_models import Incident


class IncidentRepository:
    """CRUD pour les incidents de securite."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> dict:
        """Cree un incident avec une entree dans la timeline."""
        incident = Incident(
            statut="ouverte",
            assigne_a=data.get("assigne_a"),
            alert_ids=data.get("alert_ids", []),
            rule_ids=data.get("rule_ids", []),
            mitre_attack_ids=data.get("mitre_attack_ids", []),
            notes_resolution=data.get("notes_resolution"),
            timeline=[
                {
                    "action": "created",
                    "user_id": data.get("created_by"),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "detail": "Incident cree",
                }
            ],
        )
        self.db.add(incident)
        await self.db.flush()
        await self.db.refresh(incident)
        return self._to_dict(incident)

    async def get_by_id(self, incident_id: int) -> Optional[dict]:
        """Detail d'un incident."""
        result = await self.db.execute(
            select(Incident).where(Incident.id == incident_id)
        )
        inc = result.scalar_one_or_none()
        return self._to_dict(inc) if inc else None

    async def list_incidents(
        self, statut: str = None, page: int = 1, size: int = 50
    ) -> dict:
        """Liste les incidents avec filtre par statut et pagination."""
        stmt = select(Incident).order_by(desc(Incident.cree_le))
        if statut:
            stmt = stmt.where(Incident.statut == statut)

        # Compter le total
        total_result = await self.db.execute(stmt)
        total = len(total_result.scalars().all())

        # Paginer
        result = await self.db.execute(stmt.offset((page - 1) * size).limit(size))
        items = [self._to_dict(i) for i in result.scalars().all()]

        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": max(1, (total + size - 1) // size),
        }

    async def update_status(
        self,
        incident_id: int,
        statut: str,
        user_id: int = None,
        notes: str = None,
    ) -> bool:
        """Change le statut et ajoute une entree dans la timeline."""
        result = await self.db.execute(
            select(Incident).where(Incident.id == incident_id)
        )
        inc = result.scalar_one_or_none()
        if not inc:
            return False

        old_status = inc.statut
        inc.statut = statut
        if notes:
            inc.notes_resolution = notes
        if statut in ("resolue", "classee"):
            inc.closed_at = datetime.now(timezone.utc)

        # Journalisation dans la timeline
        entry = {
            "action": "status_change",
            "from": old_status,
            "to": statut,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "detail": f"Statut passe de '{old_status}' a '{statut}'",
        }
        inc.timeline = (inc.timeline or []) + [entry]
        await self.db.flush()
        return True

    async def add_alert(
        self, incident_id: int, alert_id: int, user_id: int = None
    ) -> bool:
        """Ajoute une alerte a un incident avec journalisation."""
        result = await self.db.execute(
            select(Incident).where(Incident.id == incident_id)
        )
        inc = result.scalar_one_or_none()
        if not inc:
            return False

        if alert_id not in (inc.alert_ids or []):
            inc.alert_ids = (inc.alert_ids or []) + [alert_id]
            entry = {
                "action": "alert_added",
                "alert_id": alert_id,
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            inc.timeline = (inc.timeline or []) + [entry]
        await self.db.flush()
        return True

    async def assign(
        self, incident_id: int, user_id: int, assigned_by: int = None
    ) -> bool:
        """Assigne un incident a un analyste avec journalisation."""
        result = await self.db.execute(
            select(Incident).where(Incident.id == incident_id)
        )
        inc = result.scalar_one_or_none()
        if not inc:
            return False

        inc.assigne_a = user_id
        entry = {
            "action": "assigned",
            "user_id": assigned_by,
            "assigned_to": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        inc.timeline = (inc.timeline or []) + [entry]
        await self.db.flush()
        return True

    @staticmethod
    def _to_dict(inc: Incident) -> dict:
        return {
            "id": inc.id,
            "statut": inc.statut,
            "assigne_a": inc.assigne_a,
            "alert_ids": inc.alert_ids or [],
            "rule_ids": inc.rule_ids or [],
            "mitre_attack_ids": inc.mitre_attack_ids or [],
            "notes_resolution": inc.notes_resolution,
            "timeline": inc.timeline or [],
            "closed_at": inc.closed_at.isoformat() if inc.closed_at else None,
            "cree_le": inc.cree_le.isoformat() if inc.cree_le else None,
        }

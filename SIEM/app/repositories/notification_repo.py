# app/repositories/notification_repo.py
# -------------------------------
# Repository pour Notification — PostgreSQL

from datetime import datetime, timezone
from typing import List

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sql_models import Notification


class NotificationRepository:
    """CRUD pour les notifications utilisateur."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, user_id: int, title: str, message: str, channel: str = "in_app"
    ) -> dict:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            channel=channel,
        )
        self.db.add(notif)
        await self.db.flush()
        await self.db.refresh(notif)
        return self._to_dict(notif)

    async def get_user_notifications(
        self, user_id: int, unread_only: bool = False, limit: int = 50, offset: int = 0
    ) -> List[dict]:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(desc(Notification.created_at))
        )
        if unread_only:
            stmt = stmt.where(Notification.is_read == False)
        result = await self.db.execute(stmt.offset(offset).limit(limit))
        return [self._to_dict(n) for n in result.scalars().all()]

    async def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        result = await self.db.execute(
            select(Notification).where(
                Notification.id == notification_id, Notification.user_id == user_id
            )
        )
        notif = result.scalar_one_or_none()
        if not notif:
            return False
        notif.is_read = True
        notif.read_at = datetime.now(timezone.utc)
        await self.db.flush()
        return True

    async def mark_all_as_read(self, user_id: int) -> int:
        result = await self.db.execute(
            select(Notification).where(
                Notification.user_id == user_id, Notification.is_read == False
            )
        )
        count = 0
        for notif in result.scalars().all():
            notif.is_read = True
            notif.read_at = datetime.now(timezone.utc)
            count += 1
        await self.db.flush()
        return count

    async def count_unread(self, user_id: int) -> int:
        result = await self.db.execute(
            select(Notification).where(
                Notification.user_id == user_id, Notification.is_read == False
            )
        )
        return len(result.scalars().all())

    @staticmethod
    def _to_dict(n: Notification) -> dict:
        return {
            "id": n.id,
            "user_id": n.user_id,
            "title": n.title,
            "message": n.message,
            "channel": n.channel,
            "is_read": n.is_read,
            "read_at": n.read_at.isoformat() if n.read_at else None,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }

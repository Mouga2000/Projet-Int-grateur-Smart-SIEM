# app/repositories/audit_repo.py
# -------------------------------
# Repository pour AuditLog — PostgreSQL (SQLAlchemy)
#
# Remplacé l'ancienne version Elasticsearch.

from datetime import datetime, timezone
from typing import List

from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sql_models import AuditLog


class AuditRepository:
    """CRUD pour les logs d'audit dans PostgreSQL."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_action(self, audit_data: dict) -> dict:
        """Journalise une action utilisateur."""
        log = AuditLog(
            user_id=audit_data.get("user_id"),
            username=audit_data.get("username"),
            action=audit_data.get("action", "unknown"),
            resource_type=audit_data.get("resource_type"),
            resource_id=audit_data.get("resource_id"),
            details=audit_data.get("details"),
            ip_address=audit_data.get("ip_address", "unknown"),
            user_agent=audit_data.get("user_agent"),
            result=audit_data.get("result", "success"),
        )
        self.db.add(log)
        await self.db.flush()
        await self.db.refresh(log)
        return {
            "_id": log.id,
            "user_id": log.user_id,
            "username": log.username,
            "action": log.action,
            "result": log.result,
            "timestamp": log.created_at.isoformat() if log.created_at else None,
        }

    async def log_login_attempt(
        self, user_id: str, username: str, success: bool, ip_address: str = None
    ) -> dict:
        """Journalise une tentative de connexion."""
        return await self.log_action(
            {
                "user_id": int(user_id) if user_id and user_id != "system" else None,
                "username": username,
                "action": "login",
                "result": "success" if success else "failed",
                "ip_address": ip_address or "unknown",
                "details": {"method": "password"},
            }
        )

    async def log_logout(self, user_id: str, username: str) -> dict:
        """Journalise une déconnexion."""
        return await self.log_action(
            {
                "user_id": int(user_id) if user_id else None,
                "username": username,
                "action": "logout",
                "result": "success",
            }
        )

    async def log_mfa_verification(
        self, user_id: str, username: str, success: bool
    ) -> dict:
        """Journalise une vérification MFA."""
        return await self.log_action(
            {
                "user_id": int(user_id) if user_id else None,
                "username": username,
                "action": "mfa_verify",
                "result": "success" if success else "failed",
                "details": {"method": "totp"},
            }
        )

    async def log_user_management(
        self, admin_id: str, action: str, target_username: str, details: dict = None
    ) -> dict:
        """Journalise une action de gestion utilisateur."""
        return await self.log_action(
            {
                "user_id": int(admin_id) if admin_id else None,
                "username": target_username,
                "action": action,
                "result": "success",
                "details": details or {},
            }
        )

    async def get_audit_logs(
        self, filters: dict = None, limit: int = 100, offset: int = 0
    ) -> List[dict]:
        """Récupère les logs d'audit avec filtres."""
        stmt = (
            select(AuditLog)
            .order_by(desc(AuditLog.created_at))
            .offset(offset)
            .limit(limit)
        )

        if filters:
            for key, value in filters.items():
                column = getattr(AuditLog, key, None)
                if column is not None:
                    stmt = stmt.where(column == value)

        result = await self.db.execute(stmt)
        logs = []
        for log in result.scalars().all():
            logs.append(
                {
                    "id": log.id,
                    "user_id": log.user_id,
                    "username": log.username,
                    "action": log.action,
                    "result": log.result,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "details": log.details,
                    "ip_address": log.ip_address,
                    "timestamp": log.created_at.isoformat() if log.created_at else None,
                }
            )
        return logs

    async def delete_older_than(self, days: int) -> int:
        """Supprime les logs d'audit plus vieux que N jours dans PostgreSQL."""
        from datetime import timedelta

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = delete(AuditLog).where(AuditLog.created_at < cutoff)
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount

# app/repositories/user_repo.py
# -------------------------------
# Repository pour User — PostgreSQL (SQLAlchemy)
#
# Remplacé l'ancienne version Elasticsearch.

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from typing import Optional, List
from app.core.security import hash_password
from app.models.sql_models import User


class UserRepository:
    """CRUD pour les utilisateurs dans PostgreSQL."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: dict) -> dict:
        """Crée un nouvel utilisateur en base."""
        user = User(
            username=user_data.get("username"),
            email=user_data.get("email"),
            password_hash=hash_password(user_data.pop("password", "")),
            role=user_data.get("role", "lecteur"),
            perimeter=user_data.get("perimeter", []),
            is_active=True,
            mfa_enabled=False,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return self._to_dict(user)

    async def get_user_by_username(self, username: str) -> Optional[dict]:
        """Récupère un utilisateur par son nom d'utilisateur."""
        result = await self.db.execute(
            select(User).where(User.username == username, User.deleted_at.is_(None))
        )
        user = result.scalar_one_or_none()
        return self._to_dict(user) if user else None

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Récupère un utilisateur par son email."""
        result = await self.db.execute(
            select(User).where(User.email == email, User.deleted_at.is_(None))
        )
        user = result.scalar_one_or_none()
        return self._to_dict(user) if user else None

    async def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Récupère un utilisateur par son ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.deleted_at.is_(None))
        )
        user = result.scalar_one_or_none()
        return self._to_dict(user) if user else None

    async def update_user(self, user_id: int, update_data: dict) -> bool:
        """Met à jour un utilisateur."""
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.deleted_at.is_(None))
        )
        user = result.scalar_one_or_none()
        if not user:
            return False

        for key, value in update_data.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)

        await self.db.flush()
        return True

    async def update_last_login(self, username: str) -> bool:
        """Met à jour la date de dernière connexion."""
        result = await self.db.execute(
            select(User).where(User.username == username, User.deleted_at.is_(None))
        )
        user = result.scalar_one_or_none()
        if not user:
            return False
        user.last_login = datetime.now(timezone.utc)
        await self.db.flush()
        return True

    async def delete_user(self, username: str) -> bool:
        """Désactive un utilisateur (soft-delete)."""
        result = await self.db.execute(
            select(User).where(User.username == username, User.deleted_at.is_(None))
        )
        user = result.scalar_one_or_none()
        if not user:
            return False
        user.deleted_at = datetime.now(timezone.utc)
        user.is_active = False
        await self.db.flush()
        return True

    async def list_users(self, limit: int = 100, offset: int = 0) -> List[dict]:
        """Liste les utilisateurs actifs."""
        result = await self.db.execute(
            select(User)
            .where(User.deleted_at.is_(None))
            .order_by(User.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return [self._to_dict(u) for u in result.scalars().all()]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_dict(user: User) -> dict:
        """Convertit un modèle User en dict sérialisable."""
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "password_hash": user.password_hash,
            "mfa_secret": user.mfa_secret,
            "mfa_enabled": user.mfa_enabled,
            "role": user.role,
            "perimeter": user.perimeter or [],
            "is_active": user.is_active,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }

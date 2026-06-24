# app/repositories/base.py
# -------------------------------
# Classe de base pour les repositories PostgreSQL (SQLAlchemy async)

from typing import TypeVar, Generic, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete as sa_delete
from app.models.sql_models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Repository générique avec les opérations CRUD de base pour SQLAlchemy."""

    def __init__(self, db: AsyncSession, model: type[ModelType]):
        self.db = db
        self.model = model

    async def get(self, id: int) -> Optional[ModelType]:
        """Récupère un enregistrement par son ID."""
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict | None = None,
        order_by: Any | None = None,
    ) -> list[ModelType]:
        """Liste les enregistrements avec pagination et filtres."""
        stmt = select(self.model)

        if filters:
            for attr, value in filters.items():
                column = getattr(self.model, attr, None)
                if column is not None:
                    stmt = stmt.where(column == value)

        if order_by is not None:
            stmt = stmt.order_by(order_by)
        else:
            stmt = stmt.order_by(self.model.id.desc())

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, **kwargs) -> ModelType:
        """Crée un nouvel enregistrement."""
        obj = self.model(**kwargs)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """Met à jour un enregistrement et le retourne."""
        obj = await self.get(id)
        if obj is None:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(obj, key, value)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, id: int, soft: bool = True) -> bool:
        """Supprime un enregistrement (soft-delete par défaut)."""
        if soft:
            obj = await self.get(id)
            if obj is None:
                return False
            if hasattr(obj, "deleted_at"):
                from datetime import datetime, timezone
                obj.deleted_at = datetime.now(timezone.utc)
                await self.db.flush()
                return True
        await self.db.execute(sa_delete(self.model).where(self.model.id == id))
        await self.db.flush()
        return True

    async def count(self, filters: dict | None = None) -> int:
        """Compte les enregistrements selon les filtres."""
        stmt = select(func.count()).select_from(self.model)
        if filters:
            for attr, value in filters.items():
                column = getattr(self.model, attr, None)
                if column is not None:
                    stmt = stmt.where(column == value)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def exists(self, **kwargs) -> bool:
        """Vérifie si un enregistrement existe."""
        stmt = select(self.model)
        for attr, value in kwargs.items():
            column = getattr(self.model, attr, None)
            if column is not None:
                stmt = stmt.where(column == value)
        stmt = stmt.limit(1)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

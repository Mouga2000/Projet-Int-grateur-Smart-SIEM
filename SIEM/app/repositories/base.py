# app/repositories/base.py
# -------------------------------
# Classe de base pour les repositories (pattern Repository)
#
# Ce que tu dois mettre ici :
#
#   from sqlalchemy.ext.asyncio import AsyncSession
#   from sqlalchemy import select, func, delete as sa_delete
#   from app.models.base import Base
#
#   class BaseRepository:
#       """Repository générique avec les opérations CRUD de base."""
#
#       def __init__(self, db: AsyncSession):
#           self.db = db
#
#       async def get(self, id: int) -> Base | None:
#           """Récupère un enregistrement par son ID."""
#           pass
#
#       async def get_multi(self, skip: int = 0, limit: int = 100, filters: dict = None, order_by: str = None) -> list:
#           """Liste les enregistrements avec pagination et filtres."""
#           pass
#
#       async def create(self, obj_in: dict | Base) -> Base:
#           """Crée un nouvel enregistrement."""
#           pass
#
#       async def update(self, id: int, obj_in: dict | Base) -> Base:
#           """Met à jour un enregistrement."""
#           pass
#
#       async def delete(self, id: int, soft: bool = True) -> bool:
#           """Supprime (soft-delete par défaut) un enregistrement."""
#           pass
#
#       async def count(self, filters: dict = None) -> int:
#           """Compte les enregistrements selon les filtres."""
#           pass
#
#       async def exists(self, **kwargs) -> bool:
#           """Vérifie si un enregistrement existe."""
#           pass

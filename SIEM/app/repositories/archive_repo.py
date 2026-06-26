# app/repositories/archive_repo.py
# -------------------------------
# Repository pour Archive — PostgreSQL (SQLAlchemy)

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sql_models import Archive


class ArchiveRepository:
    """CRUD pour les archives certifiées."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> dict:
        """Crée une nouvelle archive en base."""
        archive = Archive(
            date_from=data["date_from"],
            date_to=data["date_to"],
            log_count=data["log_count"],
            file_path=data["file_path"],
            file_size_bytes=data["file_size_bytes"],
            sha256_hash=data["sha256_hash"],
            merkle_root=data["merkle_root"],
            previous_archive_id=data.get("previous_archive_id"),
            previous_hash=data.get("previous_hash"),
            chain_hash=data["chain_hash"],
            timestamp_signature=data.get("timestamp_signature"),
            certified_by=data.get("certified_by", "self"),
            certified_at=data.get("certified_at", datetime.now(timezone.utc)),
            created_by=data.get("created_by"),
            status=data.get("status", "active"),
        )
        self.db.add(archive)
        await self.db.flush()
        await self.db.refresh(archive)
        return self._to_dict(archive)

    async def get_by_id(self, archive_id: int) -> Optional[dict]:
        """Récupère une archive par son ID."""
        result = await self.db.execute(select(Archive).where(Archive.id == archive_id))
        archive = result.scalar_one_or_none()
        return self._to_dict(archive) if archive else None

    async def get_last_archive(self) -> Optional[dict]:
        """Récupère la dernière archive créée (pour la chaîne)."""
        result = await self.db.execute(
            select(Archive).order_by(desc(Archive.id)).limit(1)
        )
        archive = result.scalar_one_or_none()
        return self._to_dict(archive) if archive else None

    async def list_archives(self, limit: int = 100, offset: int = 0) -> List[dict]:
        """Liste toutes les archives triées par date de création."""
        result = await self.db.execute(
            select(Archive).order_by(desc(Archive.id)).offset(offset).limit(limit)
        )
        return [self._to_dict(a) for a in result.scalars().all()]

    async def update_verification(
        self, archive_id: int, user_id: int, status: str = "verified"
    ) -> bool:
        """Marque une archive comme vérifiée."""
        result = await self.db.execute(select(Archive).where(Archive.id == archive_id))
        archive = result.scalar_one_or_none()
        if not archive:
            return False
        archive.verified_at = datetime.now(timezone.utc)
        archive.verified_by = user_id
        archive.status = status
        await self.db.flush()
        return True

    async def count(self) -> int:
        """Compte le nombre total d'archives."""
        result = await self.db.execute(select(Archive))
        return len(result.scalars().all())

    @staticmethod
    def _to_dict(archive: Archive) -> dict:
        return {
            "id": archive.id,
            "date_from": archive.date_from.isoformat() if archive.date_from else None,
            "date_to": archive.date_to.isoformat() if archive.date_to else None,
            "log_count": archive.log_count,
            "file_path": archive.file_path,
            "file_size_bytes": archive.file_size_bytes,
            "sha256_hash": archive.sha256_hash,
            "merkle_root": archive.merkle_root,
            "previous_archive_id": archive.previous_archive_id,
            "previous_hash": archive.previous_hash,
            "chain_hash": archive.chain_hash,
            "timestamp_signature": archive.timestamp_signature,
            "certified_by": archive.certified_by,
            "certified_at": archive.certified_at.isoformat()
            if archive.certified_at
            else None,
            "created_by": archive.created_by,
            "status": archive.status,
            "verified_at": archive.verified_at.isoformat()
            if archive.verified_at
            else None,
            "verified_by": archive.verified_by,
            "created_at": archive.created_at.isoformat()
            if archive.created_at
            else None,
        }

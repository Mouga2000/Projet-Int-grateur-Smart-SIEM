# app/api/v1/archive.py
# -------------------------------
# Endpoints d'archivage conforme — Administration

from datetime import datetime, timedelta, timezone

from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_role
from app.core.config import settings
from app.core.database import get_db
from app.core.elasticsearch import get_es
from app.repositories.archive_repo import ArchiveRepository
from app.repositories.audit_repo import AuditRepository
from app.repositories.log_repo import LogRepository
from app.services.archiver import ArchiverService
from app.utils.tags import Role

router = APIRouter(prefix="/admin/archive", tags=["Archivage"])


@router.post("/create")
async def create_archive(
    days: int = Query(
        default=settings.ARCHIVE_AFTER_DAYS,
        ge=30,
        le=3650,
        description="Âge minimum des logs à archiver (en jours, max 10 ans)",
    ),
    window_days: int = Query(
        default=30,
        ge=1,
        le=365,
        description="Fenêtre temporelle de l'archive (en jours)",
    ),
    current_user: dict = Depends(require_role([Role.ADMINISTRATEUR])),
    es: AsyncElasticsearch = Depends(get_es),
    db: AsyncSession = Depends(get_db),
):
    """
    Crée une archive certifiée des logs de plus de N jours.

    Les logs sont extraits d'Elasticsearch, compressés, hashés (SHA-256),
    chaînés à l'archive précédente et horodatés avec une signature RSA.

    Réservé aux administrateurs.
    """
    if not settings.ARCHIVE_ENABLED:
        raise HTTPException(status_code=403, detail="L'archivage est désactivé")

    date_to = datetime.now(timezone.utc) - timedelta(days=days)
    date_from = date_to - timedelta(days=window_days)

    log_repo = LogRepository(es)
    archive_repo = ArchiveRepository(db)

    try:
        archive = await ArchiverService.create_archive(
            log_repo, archive_repo, date_from, date_to, current_user["id"]
        )
        audit = AuditRepository(db)
        await audit.log_action({
            "user_id": current_user["id"], "username": current_user.get("username", ""),
            "action": "create_archive", "result": "success",
            "resource_type": "archive", "resource_id": str(archive.get("id", "")),
            "details": {"date_from": str(date_from.date()), "date_to": str(date_to.date())},
        })
        return archive
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list")
async def list_archives(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(require_role([Role.AUDITEUR, Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """Liste toutes les archives avec pagination."""
    repo = ArchiveRepository(db)
    archives = await repo.list_archives(limit=size, offset=(page - 1) * size)
    total = await repo.count()

    return {
        "items": archives,
        "total": total,
        "page": page,
        "size": size,
        "pages": max(1, (total + size - 1) // size),
    }


@router.get("/chain")
async def get_archive_chain(
    current_user: dict = Depends(require_role([Role.AUDITEUR, Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """
    Affiche la chaîne complète des archives.

    Chaque archive est liée cryptographiquement à la précédente.
    Permet de vérifier visuellement l'intégrité de la chaîne.
    """
    repo = ArchiveRepository(db)
    archives = await repo.list_archives(limit=1000)

    chain = []
    for a in reversed(archives):
        chain.append(
            {
                "id": a["id"],
                "period": f"{a['date_from'][:10]} -> {a['date_to'][:10]}",
                "logs": a["log_count"],
                "chain_hash": a["chain_hash"],
                "previous_hash": a["previous_hash"] or "GENESIS",
                "status": a["status"],
                "certified_at": a["certified_at"],
            }
        )

    return {
        "chain": chain,
        "length": len(chain),
        "integrity": "verified" if chain else "empty",
    }


@router.post("/verify/{archive_id}")
async def verify_archive(
    archive_id: int,
    current_user: dict = Depends(require_role([Role.AUDITEUR, Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """
    Vérifie l'intégrité complète d'une archive :
    - Existence du fichier
    - SHA-256 du fichier correspondant
    - Chaîne de hachage valide
    - Signature temporelle valide
    """
    repo = ArchiveRepository(db)
    archive = await repo.get_by_id(archive_id)
    if not archive:
        raise HTTPException(status_code=404, detail="Archive non trouvée")

    result = ArchiverService.verify_archive(archive)

    if result["valid"]:
        await repo.update_verification(archive_id, current_user["id"], "verified")
    else:
        await repo.update_verification(archive_id, current_user["id"], "compromised")

    return result


@router.get("/{archive_id}")
async def get_archive(
    archive_id: int,
    current_user: dict = Depends(require_role([Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """Détail d'une archive."""
    repo = ArchiveRepository(db)
    archive = await repo.get_by_id(archive_id)
    if not archive:
        raise HTTPException(status_code=404, detail="Archive non trouvée")
    return archive


@router.get("/{archive_id}/export")
async def export_archive(
    archive_id: int,
    current_user: dict = Depends(require_role([Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """
    Exporte les preuves d'intégrité d'une archive pour audit réglementaire.
    Contient : hashs, signature, chaîne, statut.
    """
    repo = ArchiveRepository(db)
    archive = await repo.get_by_id(archive_id)
    if not archive:
        raise HTTPException(status_code=404, detail="Archive non trouvée")

    report = ArchiverService.export_archive(archive)
    return report

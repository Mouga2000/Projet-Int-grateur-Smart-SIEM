# app/api/v1/logs.py
# -------------------------------
# Endpoints /api/v1/logs — Gestion des logs

from datetime import datetime

from elasticsearch import ConnectionError as ESConnectionError
from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.api.dependencies import get_current_user
from app.core.elasticsearch import get_es
from app.repositories.log_repo import LogRepository
from app.schemas.log_schemas import LogListResponse, LogResponse, LogSearchRequest
from app.services.normalization import NormalizationService

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.post("/ingest", response_model=LogResponse)
async def ingest_log(
    request: Request,
    es=Depends(get_es),
):
    """
    Point d'entrée universel — accepte tout JSON, quel que soit le format.
    """
    raw_data = await request.json()
    import json

    try:
        normalized = await NormalizationService.normalize(raw_data)

        print(f"\n{'=' * 60}")
        print(f"RAW -> NORMALIZED ({datetime.now().strftime('%H:%M:%S')})")
        print(f"{'=' * 60}")
        print("RAW:")
        print(json.dumps(raw_data, indent=2, ensure_ascii=False, default=str)[:500])
        print(f"\n{'-' * 40}")
        print("NORMALIZED (stocke dans ES) :")
        print(json.dumps(normalized, indent=2, ensure_ascii=False, default=str))
        print(f"{'=' * 60}\n")
        repo = LogRepository(es)
        result = await repo.ingest(normalized)

        return LogResponse(
            id=result["id"],
            timestamp=normalized["timestamp"],
            source_ip=normalized["source_ip"],
            host=normalized["host"],
            log_type=normalized.get("log_type"),
            severity=normalized["severity"],
            raw_message=normalized["raw_message"],
            tags=normalized.get("tags", []),
        )

    except ESConnectionError:
        raise HTTPException(status_code=503, detail="Elasticsearch indisponible")


@router.get("/", response_model=LogListResponse)
async def list_logs(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    es=Depends(get_es),
):
    """Liste les logs avec pagination (du plus récent au plus ancien)."""
    repo = LogRepository(es)
    return await repo.search(page=page, size=size)


@router.post("/search", response_model=LogListResponse)
async def search_logs(
    search: LogSearchRequest,
    current_user: dict = Depends(get_current_user),
    es=Depends(get_es),
):
    """
    Recherche multi-criteres dans les logs.

    Filtres disponibles :
    - query : recherche plein texte dans raw_message
    - source_ips : filtrer par IP source
    - destination_ips : filtrer par IP destination (extraite du message)
    - users : filtrer par nom d'utilisateur (extrait du message)
    - hosts : filtrer par nom de machine
    - log_types : filtrer par type (auth, reseau, systeme, application)
    - severities : filtrer par criticite (info, warning, error, critical)
    - date_from / date_to : plage horaire
    """
    repo = LogRepository(es)

    must_clauses = []

    if search.query != "*":
        must_clauses.append(
            {
                "query_string": {
                    "query": search.query,
                    "default_field": "raw_message",
                }
            }
        )

    if search.source_ips:
        must_clauses.append({"terms": {"source_ip": search.source_ips}})

    if search.destination_ips:
        must_clauses.append({"terms": {"decoded.ips": search.destination_ips}})

    if search.users:
        must_clauses.append({"terms": {"decoded.user": search.users}})

    if search.hosts:
        must_clauses.append({"terms": {"host": search.hosts}})

    if search.log_types:
        must_clauses.append({"terms": {"log_type": search.log_types}})

    if search.severities:
        must_clauses.append({"terms": {"severity": search.severities}})

    if search.tags:
        must_clauses.append({"terms": {"tags": search.tags}})

    if search.date_from or search.date_to:
        range_filter = {}
        if search.date_from:
            range_filter["gte"] = search.date_from.isoformat()
        if search.date_to:
            range_filter["lte"] = search.date_to.isoformat()
        must_clauses.append({"range": {"timestamp": range_filter}})

    es_query = {"bool": {"must": must_clauses}} if must_clauses else {"match_all": {}}

    result = await repo.search(query=es_query, page=search.page, size=search.size)
    return result


@router.get("/{log_id}", response_model=LogResponse)
async def get_log(
    log_id: str,
    current_user: dict = Depends(get_current_user),
    es=Depends(get_es),
):
    """Récupère un log par son ID Elasticsearch."""
    repo = LogRepository(es)
    log = await repo.get_by_id(log_id)

    if not log:
        raise HTTPException(status_code=404, detail="Log non trouvé")

    return LogResponse(
        id=log["id"],
        timestamp=log.get("timestamp"),
        source_ip=log.get("source_ip", "0.0.0.0"),
        host=log.get("host", "unknown"),
        log_type=log.get("log_type"),
        severity=log.get("severity", "info"),
        raw_message=log.get("raw_message", ""),
        tags=log.get("tags", []),
    )


@router.delete("/{log_id}", status_code=204)
async def delete_log(
    log_id: str,
    current_user: dict = Depends(get_current_user),
    es=Depends(get_es),
):
    """Supprime un log par son ID Elasticsearch."""
    repo = LogRepository(es)
    try:
        await repo.es.delete(
            index=f"{repo.index_prefix}-*",
            id=log_id,
            refresh=True,
        )
    except Exception:
        raise HTTPException(status_code=404, detail="Log non trouvé")

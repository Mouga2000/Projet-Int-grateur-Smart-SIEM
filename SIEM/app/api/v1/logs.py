# app/api/v1/logs.py
# -------------------------------
# Endpoints /api/v1/logs — Gestion des logs

from datetime import datetime
from typing import Optional

from elasticsearch import ConnectionError as ESConnectionError
import json

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.elasticsearch import get_es
from app.core.redis import get_redis
from app.repositories.log_repo import LogRepository
from app.schemas.log_schemas import LogListResponse, LogResponse, LogSearchRequest
from app.services.normalization import NormalizationService

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.post("/ingest")
async def ingest_log(
    request: Request,
    es=Depends(get_es),
    db: AsyncSession = Depends(get_db),
):
    """
    Point d'entree universel pour les logs.

    Accepte deux formats :
      - Un objet JSON (dict)  → normalisation + indexation + correlation
      - Un tableau JSON (list) → normalisation + bulk index (imports massifs)
    """
    raw_data = await request.json()

    # ── Mode bulk : un tableau de logs ──
    if isinstance(raw_data, list):
        if not raw_data:
            return {"indexed": 0, "total": 0}

        repo = LogRepository(es)
        normalized_logs = []
        errors = []

        for i, item in enumerate(raw_data):
            try:
                normalized = await NormalizationService.normalize(item)
                normalized_logs.append(normalized)
            except Exception as e:
                errors.append({"index": i, "error": str(e)[:200]})

        if not normalized_logs:
            return {"indexed": 0, "total": len(raw_data), "errors": errors}

        try:
            result = await repo.bulk_ingest(normalized_logs)
            indexed_count = sum(
                1 for item in result.get("indexed", [])
                if item.get("index", {}).get("status") in (200, 201)
            )
        except ESConnectionError:
            raise HTTPException(status_code=503, detail="Elasticsearch indisponible")

        return {
            "indexed": indexed_count,
            "total": len(raw_data),
            "errors": errors,
        }

    # ── Mode simple : un seul log (comportement historique) ──
    try:
        normalized = await NormalizationService.normalize(raw_data)

        repo = LogRepository(es)
        result = await repo.ingest(normalized)

        # UEBA : scoring temps réel (asynchrone via Celery)
        try:
            if settings.UEBA_ENABLED:
                from app.tasks.ueba_tasks import score_single_event

                score_single_event.delay(normalized)
        except Exception as e:
            print(f"[UEBA] Erreur scoring temps reel : {e}")

        # Correlation
        try:
            from app.repositories.alert_repo import AlertRepository
            from app.repositories.rule_repo import RuleRepository
            from app.repositories.user_repo import UserRepository
            from app.services.correlation import CorrelationEngine

            rule_repo = RuleRepository(db)
            alert_repo = AlertRepository(db)
            user_repo = UserRepository(db)
            engine = CorrelationEngine(
                rule_repository=rule_repo,
                alert_repository=alert_repo,
                elastic_repository=repo,
                redis_client=None,
                user_repository=user_repo,
            )
            alerts_created = await engine.evaluate_event(normalized)
            if alerts_created:
                print(f"[CORRELATION] {alerts_created} alerte(s) creee(s)")
        except Exception as e:
            print(f"[CORRELATION] Erreur : {e}")

        return {
            "id": result["id"],
            "timestamp": normalized["timestamp"],
            "source_ip": normalized["source_ip"],
            "host": normalized["host"],
            "log_type": normalized.get("log_type"),
            "severity": normalized["severity"],
            "raw_message": normalized["raw_message"],
            "tags": normalized.get("tags", []),
        }

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
    from elasticsearch import ConnectionError as ESConnError

    # Cache Redis 15s : éviter de saturer ES sur les refreshes rapides
    cache_key = f"dashboard:logs:{page}:{size}"
    redis = None
    try:
        redis = await get_redis()
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception:
        pass  # Redis indisponible → on passe sans cache

    repo = LogRepository(es)
    try:
        result = await repo.search(page=page, size=size)
        if redis:
            try:
                await redis.setex(cache_key, 15, json.dumps(result, default=str))
            except Exception:
                pass
        return result
    except ESConnError:
        return {"items": [], "total": 0, "page": page, "size": size, "pages": 0}


@router.get("/severity-distribution")
async def get_severity_distribution(
    current_user: dict = Depends(get_current_user),
    es=Depends(get_es),
):
    """Retourne la répartition des logs par sévérité (sur TOUS les logs)."""
    repo = LogRepository(es)
    result = await repo.severity_distribution()
    return result


@router.get("/top/{field}")
async def get_top_field(
    field: str,
    size: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    es=Depends(get_es),
):
    """
    Retourne les N valeurs les plus fréquentes d'un champ.
    Utilisé par le Dashboard : top hosts, top IPs, top log_types.
    Exemples : /logs/top/host?size=6, /logs/top/source_ip?size=6
    """
    repo = LogRepository(es)
    result = await repo.top_field(field, size)
    return result


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

    # Filtre automatique par perimetre de l'utilisateur
    user_perimeter = current_user.get("perimeter", [])
    user_role = current_user.get("role")
    should_clauses = []
    if user_perimeter and user_role != "administrateur":
        perimeter_filters = []
        for p in user_perimeter:
            if p == "equipe":
                perimeter_filters.append({"term": {"tags": "equipe"}})
            elif p == "service":
                perimeter_filters.append({"term": {"tags": "service"}})
            elif p == "filiale":
                perimeter_filters.append({"term": {"tags": "filiale"}})
            elif p == "environnement":
                perimeter_filters.append({"term": {"tags": "environnement"}})

        if perimeter_filters:
            should_clauses.extend(perimeter_filters)

    # Construire la query ES
    if must_clauses:
        es_query = {"bool": {"must": must_clauses}}
    else:
        es_query = {"bool": {"must": [{"match_all": {}}]}}

    if should_clauses:
        es_query["bool"]["should"] = should_clauses
        es_query["bool"]["minimum_should_match"] = 0

    result = await repo.search(query=es_query, page=search.page, size=search.size)
    return result


@router.get("/timeline")
async def get_timeline(
    interval: str = Query(
        default="1h",
        pattern="^(10s|30s|1m|5m|15m|30m|1h|6h|12h|1d|1w|1M)$",
        description="Intervalle de l'histogramme (10s, 1m, 1h, 1d, 1w, 1M)",
    ),
    date_from: Optional[datetime] = Query(
        default=None, description="Debut de la plage horaire"
    ),
    date_to: Optional[datetime] = Query(
        default=None, description="Fin de la plage horaire"
    ),
    severities: Optional[str] = Query(
        default=None,
        description="Filtrer par severites (separes par des virgules : critical,error,warning)",
    ),
    current_user: dict = Depends(get_current_user),
    es=Depends(get_es),
):
    """
    Retourne une serie temporelle pour alimenter un graphique chronologique.

    Utilise l'aggregation date_histogram d'Elasticsearch pour grouper
    les logs par intervalles (10s, 1m, 1h, 1d, ...) sans charger tous les documents.

    Exemple de reponse :
    {
        "timeline": [
            {"timestamp": "2026-06-27T10:00:00.000Z", "count": 42},
            {"timestamp": "2026-06-27T11:00:00.000Z", "count": 15},
            ...
        ],
        "total": 1250,
        "interval": "1h",
        "bucket_count": 24
    }
    """
    from elasticsearch import ConnectionError as ESConnError

    # Cache Redis 30s : la timeline est la requête la plus lourde
    cache_key = f"dashboard:timeline:{interval}:{severities or 'all'}"
    redis = None
    try:
        redis = await get_redis()
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception:
        pass

    repo = LogRepository(es)
    severity_list = severities.split(",") if severities else None

    try:
        result = await repo.search_timeline(
            interval=interval,
            date_from=date_from,
            date_to=date_to,
            severity_filter=severity_list,
        )
        if redis:
            try:
                await redis.setex(cache_key, 30, json.dumps(result, default=str))
            except Exception:
                pass
        return result
    except ESConnError:
        return {"timeline": [], "total": 0, "interval": interval, "bucket_count": 0}


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

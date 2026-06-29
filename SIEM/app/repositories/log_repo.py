# app/repositories/log_repo.py
# -------------------------------
# Repository pour Log — index ES "logs-YYYY-MM-DD"

from datetime import datetime
from typing import List, Optional

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError

from app.core.config import settings


class LogRepository:
    """CRUD pour les logs de sécurité dans Elasticsearch."""

    def __init__(self, es: AsyncElasticsearch):
        self.es = es
        self.index_prefix = settings.ELASTICSEARCH_INDEX_LOGS

    def _get_index_name(self, date: datetime = None) -> str:
        """Retourne le nom de l'index pour la date donnée (logs-YYYY-MM-DD)."""
        today = (date or datetime.now()).strftime("%Y-%m-%d")
        return f"{self.index_prefix}-{today}"

    async def ingest(self, log_data: dict) -> dict:
        """Indexe un log dans Elasticsearch et retourne le document avec son ID."""
        response = await self.es.index(
            index=self._get_index_name(),
            body=log_data,
            refresh=True,
        )
        log_data["id"] = response["_id"]
        return log_data

    async def bulk_ingest(self, logs: list[dict]) -> dict:
        """Indexe plusieurs logs en une requête bulk."""
        if not logs:
            return {"indexed": 0, "errors": []}

        bulk_body = []
        for log in logs:
            bulk_body.append({"index": {"_index": self._get_index_name()}})
            bulk_body.append(log)

        response = await self.es.bulk(body=bulk_body, refresh=True)

        return {
            "indexed": response.get("items", []),
            "errors": response.get("errors", False),
        }

    async def get_by_id(self, log_id: str) -> Optional[dict]:
        """Récupère un log par son ID Elasticsearch."""
        try:
            response = await self.es.get(
                index=f"{self.index_prefix}-*",
                id=log_id,
            )
            doc = response["_source"]
            doc["id"] = response["_id"]
            return doc
        except NotFoundError:
            return None

    async def search(
        self,
        query: dict = None,
        page: int = 1,
        size: int = 50,
        index: str = None,
    ) -> dict:
        """
        Recherche des logs avec la query DSL Elasticsearch.

        Args:
            query: Requête Elasticsearch DSL.
            page: Numéro de page (1-indexé).
            size: Taille de page.
            index: Index ES cible (défaut: logs-*).
                   Utiliser 'logs-clue' pour les données CLUE-LDS.
        """
        if query is None:
            query = {"match_all": {}}

        body = {
            "query": query,
            "from": (page - 1) * size,
            "size": size,
            "sort": [{"timestamp": {"order": "desc"}}],
        }

        target_index = index or f"{self.index_prefix}-*"
        response = await self.es.search(
            index=target_index,
            body=body,
        )

        hits = response["hits"]["hits"]
        total = response["hits"]["total"]["value"]

        items = []
        for hit in hits:
            doc = hit["_source"]
            doc["id"] = hit["_id"]
            items.append(doc)

        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": max(1, (total + size - 1) // size),
        }

    async def search_by_date_range(
        self, date_from: datetime, date_to: datetime, size: int = 10000
    ) -> dict:
        """Recherche tous les logs dans une plage de dates (pour archivage)."""
        query = {
            "range": {
                "timestamp": {
                    "gte": date_from.isoformat(),
                    "lte": date_to.isoformat(),
                }
            }
        }
        # Utiliser un scroll pour récupérer tous les logs
        response = await self.es.search(
            index=f"{self.index_prefix}-*",
            body={
                "query": query,
                "size": size,
                "sort": [{"timestamp": {"order": "asc"}}],
            },
            scroll="2m",
        )

        hits = response["hits"]["hits"]
        total = response["hits"]["total"]["value"]

        items = []
        for hit in hits:
            doc = hit["_source"]
            doc["id"] = hit["_id"]
            items.append(doc)

        # Si plus de résultats que size, continuer avec le scroll
        scroll_id = response.get("_scroll_id")
        while len(items) < total and scroll_id:
            scroll_response = await self.es.scroll(scroll_id=scroll_id, scroll="2m")
            scroll_hits = scroll_response["hits"]["hits"]
            if not scroll_hits:
                break
            for hit in scroll_hits:
                doc = hit["_source"]
                doc["id"] = hit["_id"]
                items.append(doc)
            scroll_id = scroll_response.get("_scroll_id")

        # Nettoyer le scroll
        if scroll_id:
            try:
                await self.es.clear_scroll(scroll_id=scroll_id)
            except Exception:
                pass

        return {
            "items": items,
            "total": total,
        }

    async def count(self, query: dict = None) -> int:
        """Compte les logs correspondant à une requête."""
        if query is None:
            query = {"match_all": {}}

        response = await self.es.count(
            index=f"{self.index_prefix}-*",
            body={"query": query},
        )
        return response["count"]

    async def delete_older_than(self, days: int) -> int:
        """Supprime les logs plus vieux que N jours via delete_by_query."""
        response = await self.es.delete_by_query(
            index=f"{self.index_prefix}-*",
            body={
                "query": {
                    "range": {
                        "timestamp": {
                            "lte": f"now-{days}d",
                        }
                    }
                }
            },
            refresh=True,
        )
        return response.get("deleted", 0)

    async def search_timeline(
        self,
        interval: str = "1h",
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        severity_filter: Optional[List[str]] = None,
    ) -> dict:
        """
        Agrégation date_histogram pour construire une timeline interactive.

        Regroupe les logs par intervalles de temps et retourne les compteurs
        pour alimenter un graphique chronologique.
        """
        must_clauses = []

        # Filtre temporel
        if date_from or date_to:
            range_filter = {}
            if date_from:
                range_filter["gte"] = date_from.isoformat()
            if date_to:
                range_filter["lte"] = date_to.isoformat()
            must_clauses.append({"range": {"timestamp": range_filter}})

        # Filtre optionnel par severite
        if severity_filter:
            must_clauses.append({"terms": {"severity": severity_filter}})

        query = {"bool": {"must": must_clauses}} if must_clauses else {"match_all": {}}

        # Agrégation date_histogram
        body = {
            "query": query,
            "size": 0,  # On ne veut que les aggregations, pas les documents
            "aggs": {
                "events_over_time": {
                    "date_histogram": {
                        "field": "timestamp",
                        "fixed_interval": interval,
                        "min_doc_count": 1,
                    }
                },
                "total_count": {"value_count": {"field": "timestamp"}},
            },
        }

        response = await self.es.search(
            index=f"{self.index_prefix}-*",
            body=body,
        )

        buckets = response["aggregations"]["events_over_time"]["buckets"]
        total = response["aggregations"]["total_count"]["value"]

        timeline = [
            {
                "timestamp": b["key_as_string"],
                "count": b["doc_count"],
            }
            for b in buckets
        ]

        return {
            "timeline": timeline,
            "total": total,
            "interval": interval,
            "bucket_count": len(timeline),
        }

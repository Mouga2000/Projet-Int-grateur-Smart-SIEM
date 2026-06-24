# app/repositories/log_repo.py
# -------------------------------
# Repository pour Log — index ES "logs-YYYY-MM-DD"

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError, ConnectionError as ESConnectionError
from datetime import datetime
from typing import Optional, List
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
    ) -> dict:
        """Recherche des logs avec la query DSL Elasticsearch."""
        if query is None:
            query = {"match_all": {}}

        body = {
            "query": query,
            "from": (page - 1) * size,
            "size": size,
            "sort": [{"timestamp": {"order": "desc"}}],
        }

        response = await self.es.search(
            index=f"{self.index_prefix}-*",
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
        cutoff = datetime.now().isoformat()
        # On cible les index datés pour le delete
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

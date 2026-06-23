# app/services/search.py
# -------------------------------
# Service de recherche Elasticsearch
#
# Ce que tu dois mettre ici :
#
#   from elasticsearch import AsyncElasticsearch
#   from app.core.elasticsearch import get_es_client
#
#   class SearchService:
#       """Recherche plein texte et structurée dans Elasticsearch."""
#
#       INDEX_NAME = "siem-logs-*"  # Utilise un alias ou pattern d'index daté
#
#       async def search(self, query: dict) -> dict:
#           """Exécute une requête Elasticsearch."""
#           pass
#
#       async def get_by_id(self, log_id: str) -> dict:
#           """Récupère un document par son ID Elasticsearch."""
#           pass
#
#       async def count(self, query: dict) -> int:
#           """Compte le nombre de documents correspondant à la requête."""
#           pass
#
#       async def aggregate(self, query: dict, aggs: dict) -> dict:
#           """Exécute des agrégations Elasticsearch."""
#           pass
#
#       async def suggest(self, field: str, prefix: str, size: int = 10) -> list:
#           """Auto-complétion sur un champ."""
#           pass
#
#       async def save_search(self, user_id: int, name: str, query: dict):
#           """Sauvegarde une recherche pour un utilisateur."""
#           pass
#
#       async def get_saved_searches(self, user_id: int) -> list:
#           """Récupère les recherches sauvegardées d'un utilisateur."""
#           pass

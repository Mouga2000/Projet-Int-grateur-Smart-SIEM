# app/core/elasticsearch.py
# -------------------------------
# Connexion Elasticsearch asynchrone
#
# Ce que tu dois mettre ici :
#
#   from elasticsearch import AsyncElasticsearch
#   from app.core.config import settings
#
#   # Client Elasticsearch asynchrone
#   es_client: AsyncElasticsearch | None = None
#
#   async def get_es_client() -> AsyncElasticsearch:
#       """Retourne le client ES (créé au startup)."""
#       global es_client
#       if es_client is None:
#           es_client = AsyncElasticsearch(
#               hosts=[settings.ELASTICSEARCH_HOSTS],
#               basic_auth=(
#                   (settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD)
#                   if settings.ELASTICSEARCH_USER
#                   else None
#               ),
#           )
#       return es_client
#
#   async def init_es():
#       """Vérifie que ES est accessible au démarrage."""
#       client = await get_es_client()
#       if not await client.ping():
#           raise ConnectionError("Elasticsearch is not reachable")
#
#   async def close_es():
#       """Ferme le client au shutdown."""
#       global es_client
#       if es_client:
#           await es_client.close()
#           es_client = None
#
# Note : Elasticsearch sert de base de données centralisée pour tout le projet
#         (utilisateurs, audit, logs, alertes, règles, etc.)

from elasticsearch import AsyncElasticsearch
from app.core.config import settings

class ElasticsearchClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = AsyncElasticsearch(
                hosts=[f"{settings.ELASTICSEARCH_SCHEME}://{settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}"]
            )
        return cls._instance

async def get_es() -> AsyncElasticsearch:
    return ElasticsearchClient()

# Fonction utilitaire pour vérifier l'index
async def ensure_index(es: AsyncElasticsearch, index: str, mapping: dict):
    """Crée l'index s'il n'existe pas"""
    if not await es.indices.exists(index=index):
        await es.indices.create(index=index, body=mapping)
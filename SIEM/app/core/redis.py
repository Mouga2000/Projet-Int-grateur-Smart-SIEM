# app/core/redis.py
# -------------------------------
# Connexion Redis (cache, files d'attente Celery, rate limiting)
#
# Ce que tu dois mettre ici :
#
#   import redis.asyncio as aioredis
#   from app.core.config import settings
#
#   redis_client: aioredis.Redis | None = None
#
#   async def get_redis() -> aioredis.Redis:
#       """Retourne le client Redis (initialisé au startup)."""
#       global redis_client
#       if redis_client is None:
#           redis_client = aioredis.from_url(
#               f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
#               password=settings.REDIS_PASSWORD or None,
#               decode_responses=True,
#           )
#       return redis_client
#
#   async def close_redis():
#       global redis_client
#       if redis_client:
#           await redis_client.aclose()
#           redis_client = None
#
#   # Dépendance FastAPI
#   async def get_cache() -> aioredis.Redis:
#       return await get_redis()
#
# Utilisations de Redis dans le SIEM :
#   - Cache des sessions / tokens JWT révoqués
#   - Rate limiting (sliding window)
#   - File d'attente Celery (broker)
#   - Stockage temporaire des résultats de recherche
#   - Compteurs pour la détection de bruteforce

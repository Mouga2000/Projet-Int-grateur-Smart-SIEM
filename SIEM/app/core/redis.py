# app/core/redis.py
# -------------------------------
# Connexion Redis (cache, compteurs de seuil, files d'attente Celery)

import redis.asyncio as aioredis

from app.core.config import settings

redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """Retourne le client Redis (initialise au premier appel)."""
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
            decode_responses=True,
        )
    return redis_client


async def close_redis():
    """Ferme la connexion au shutdown."""
    global redis_client
    if redis_client:
        await redis_client.aclose()
        redis_client = None


async def get_cache() -> aioredis.Redis:
    return await get_redis()

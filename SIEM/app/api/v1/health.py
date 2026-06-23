# app/api/v1/health.py
# -------------------------------
# Endpoints /api/v1/health — Health check & monitoring
#
# Ce que tu dois mettre ici :
#
#   from fastapi import APIRouter
#   from pydantic import BaseModel
#
#   router = APIRouter()
#
#   class HealthResponse(BaseModel):
#       status: str
#       version: str
#       database: str
#       elasticsearch: str
#       redis: str
#
#   @router.get("/", response_model=HealthResponse)
#   async def health_check():
#       """
#       Health check principal. Vérifie :
#       - Connexion PostgreSQL (SELECT 1)
#       - Connexion Elasticsearch (ping)
#       - Connexion Redis (ping)
#       """
#       return {
#           "status": "ok",
#           "version": "1.0.0",
#           "database": "connected",
#           "elasticsearch": "connected",
#           "redis": "connected",
#       }
#
#   @router.get("/ready")
#   async def readiness():
#       """Readiness probe (pour Kubernetes)."""
#       pass
#
#   @router.get("/live")
#   async def liveness():
#       """Liveness probe (pour Kubernetes)."""
#       return {"status": "alive"}

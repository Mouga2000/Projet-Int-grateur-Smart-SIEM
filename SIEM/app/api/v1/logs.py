# app/api/v1/logs.py
# -------------------------------
# Endpoints /api/v1/logs — Gestion des logs
#
# Ce que tu dois mettre ici :
#
#   from fastapi import APIRouter, Depends, Query
#   from app.schemas.log_schemas import LogCreate, LogResponse, LogListResponse
#   from app.services.normalization import NormalizationService
#   from app.api.dependencies import get_current_user
#
#   router = APIRouter()
#
#   @router.post("/ingest", response_model=LogResponse)
#   async def ingest_log(log: LogCreate):
#       """Endpoint de réception des logs (format JSON, Syslog, etc.)."""
#       pass
#
#   @router.get("/", response_model=LogListResponse)
#   async def list_logs(
#       page: int = Query(1, ge=1),
#       size: int = Query(50, le=1000),
#       current_user = Depends(get_current_user),
#   ):
#       """Liste les logs avec pagination."""
#       pass
#
#   @router.get("/{log_id}", response_model=LogResponse)
#   async def get_log(log_id: str, current_user = Depends(get_current_user)):
#       """Récupère un log par son ID (Elasticsearch)."""
#       pass
#
#   @router.delete("/{log_id}", status_code=204)
#   async def delete_log(log_id: str, current_user = Depends(get_current_user)):
#       """Supprime un log (soft-delete ou purge ES)."""
#       pass

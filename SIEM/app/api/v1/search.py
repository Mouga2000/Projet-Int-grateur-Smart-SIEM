# app/api/v1/search.py
# -------------------------------
# Endpoints /api/v1/search — Recherche avancée dans les logs
#
# Ce que tu dois mettre ici :
#
#   from fastapi import APIRouter, Depends, Body
#   from app.schemas.search_schemas import SearchRequest, SearchResponse
#   from app.services.search import SearchService
#   from app.api.dependencies import get_current_user
#
#   router = APIRouter()
#
#   @router.post("/", response_model=SearchResponse)
#   async def search_logs(
#       query: SearchRequest,
#       current_user = Depends(get_current_user),
#   ):
#       """
#       Recherche plein texte avec filtres.
#       Supporte : Elasticsearch query DSL, filtres temporels,
#       filtres par source, tags MITRE ATT&CK, etc.
#       """
#       pass
#
#   @router.post("/save")
#   async def save_search(
#       query: SearchRequest,
#       name: str,
#       current_user = Depends(get_current_user),
#   ):
#       """Sauvegarde une recherche pour réutilisation."""
#       pass
#
#   @router.get("/saved")
#   async def list_saved_searches(current_user = Depends(get_current_user)):
#       """Liste les recherches sauvegardées."""
#       pass

# app/api/v1/alerts.py
# -------------------------------
# Endpoints /api/v1/alerts — Gestion des alertes
#
# Ce que tu dois mettre ici :
#
#   from fastapi import APIRouter, Depends, Query
#   from app.schemas.alert_schemas import AlertResponse, AlertListResponse, AlertUpdate
#   from app.services.alerts import AlertService
#   from app.api.dependencies import get_current_user
#
#   router = APIRouter()
#
#   @router.get("/", response_model=AlertListResponse)
#   async def list_alerts(
#       status: str = Query(None, regex="^(open|in_progress|resolved|dismissed)$"),
#       severity: str = Query(None, regex="^(low|medium|high|critical)$"),
#       page: int = Query(1, ge=1),
#       size: int = Query(50, le=200),
#       current_user = Depends(get_current_user),
#   ):
#       """Liste les alertes avec filtres."""
#       pass
#
#   @router.get("/{alert_id}", response_model=AlertResponse)
#   async def get_alert(alert_id: int, current_user = Depends(get_current_user)):
#       """Détail d'une alerte."""
#       pass
#
#   @router.patch("/{alert_id}", response_model=AlertResponse)
#   async def update_alert(
#       alert_id: int,
#       data: AlertUpdate,
#       current_user = Depends(get_current_user),
#   ):
#       """Mettre à jour le statut / assignation d'une alerte."""
#       pass
#
#   @router.post("/{alert_id}/acknowledge")
#   async def acknowledge_alert(alert_id: int, current_user = Depends(get_current_user)):
#       """Accuser réception d'une alerte."""
#       pass
#
#   @router.post("/{alert_id}/escalate")
#   async def escalate_alert(alert_id: int, current_user = Depends(get_current_user)):
#       """Escalader une alerte (changer criticité, notifier)."""
#       pass

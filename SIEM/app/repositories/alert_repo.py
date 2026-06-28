# app/repositories/alert_repo.py
# -------------------------------
# Repository pour Alert — index ES "alerts"
#
# Ce que tu dois mettre ici :
#
#   from elasticsearch import AsyncElasticsearch
#   from typing import Optional, List
#   from app.core.config import settings
#
#   class AlertRepository:
#       """CRUD pour les alertes dans Elasticsearch."""
#
#       def __init__(self, es: AsyncElasticsearch):
#           self.es = es
#           self.index = settings.ELASTICSEARCH_INDEX_ALERTS
#
#       async def create(self, alert_data: dict) -> dict:
#           """Crée une alerte."""
#           pass
#
#       async def get_by_id(self, alert_id: str) -> Optional[dict]:
#           """Récupère une alerte par son ID."""
#           pass
#
#       async def search(self, filters: dict = None, page: int = 1, size: int = 50) -> dict:
#           """Liste les alertes avec filtres (status, severity, date)."""
#           pass
#
#       async def update(self, alert_id: str, update_data: dict) -> bool:
#           """Met à jour le statut / assignation d'une alerte."""
#           pass
#
#       async def get_stats_by_severity(self) -> list[dict]:
#           """Agrégation : nombre d'alertes par sévérité."""
#           pass
#
#       async def get_stats_by_status(self) -> list[dict]:
#           """Agrégation : nombre d'alertes par statut."""
#           pass

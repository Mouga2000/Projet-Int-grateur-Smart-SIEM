# app/repositories/incident_repo.py
# -------------------------------
# Repository pour Incident — index ES "incidents"
#
# Ce que tu dois mettre ici :
#
#   from elasticsearch import AsyncElasticsearch
#   from typing import Optional, List
#   from app.core.config import settings
#
#   class IncidentRepository:
#       """CRUD pour les incidents dans Elasticsearch."""
#
#       def __init__(self, es: AsyncElasticsearch):
#           self.es = es
#           self.index = settings.ELASTICSEARCH_INDEX_INCIDENTS
#
#       async def create(self, incident_data: dict) -> dict:
#           pass
#
#       async def get_by_id(self, incident_id: str) -> Optional[dict]:
#           pass
#
#       async def get_active(self) -> List[dict]:
#           """Incidents non clos."""
#           pass
#
#       async def search(self, filters: dict = None) -> dict:
#           pass
#
#       async def update(self, incident_id: str, update_data: dict) -> bool:
#           pass
#
#       async def add_to_timeline(self, incident_id: str, entry: dict) -> bool:
#           """Ajoute une entrée à la chronologie de l'incident."""
#           pass
#
#       async def link_alert(self, incident_id: str, alert_id: str) -> bool:
#           """Associe une alerte à un incident."""
#           pass

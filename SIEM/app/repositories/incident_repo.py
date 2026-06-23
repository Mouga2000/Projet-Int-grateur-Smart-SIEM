# app/repositories/incident_repo.py
# -------------------------------
# Repository pour Incident
#
# Ce que tu dois mettre ici :
#
#   from app.repositories.base import BaseRepository
#   from app.models.incident import Incident
#
#   class IncidentRepository(BaseRepository):
#       """CRUD pour les incidents."""
#
#       def __init__(self, db):
#           super().__init__(db)
#           self.model = Incident
#
#       async def get_active_incidents(self) -> list[Incident]:
#           """Incidents non clos."""
#           pass
#
#       async def get_by_status(self, status: str) -> list[Incident]:
#           pass
#
#       async def get_by_severity(self, severity: str) -> list[Incident]:
#           pass
#
#       async def link_alert(self, incident_id: int, alert_id: int):
#           """Associe une alerte à un incident."""
#           pass

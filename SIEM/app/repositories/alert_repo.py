# app/repositories/alert_repo.py
# -------------------------------
# Repository pour Alert
#
# Ce que tu dois mettre ici :
#
#   from app.repositories.base import BaseRepository
#   from app.models.alert import Alert
#   from typing import Optional
#
#   class AlertRepository(BaseRepository):
#       """CRUD pour les alertes."""
#
#       def __init__(self, db):
#           super().__init__(db)
#           self.model = Alert
#
#       async def get_by_status(self, status: str, skip: int = 0, limit: int = 50) -> list[Alert]:
#           pass
#
#       async def get_by_severity(self, severity: str, skip: int = 0, limit: int = 50) -> list[Alert]:
#           pass
#
#       async def get_by_rule(self, rule_id: int) -> list[Alert]:
#           pass
#
#       async def get_open_alerts_count(self) -> int:
#           pass
#
#       async def get_alerts_by_date_range(self, date_from, date_to) -> list[Alert]:
#           pass
#
#       async def get_stats_by_severity(self) -> list[dict]:
#           """Retourne le nombre d'alertes par sévérité."""
#           pass

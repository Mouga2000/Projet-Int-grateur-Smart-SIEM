# app/repositories/log_repo.py
# -------------------------------
# Repository pour LogMetadata (métadonnées des logs en PostgreSQL)
#
# Ce que tu dois mettre ici :
#
#   from app.repositories.base import BaseRepository
#   from app.models.log import LogMetadata
#
#   class LogRepository(BaseRepository):
#       """CRUD pour les métadonnées de logs."""
#
#       def __init__(self, db):
#           super().__init__(db)
#           self.model = LogMetadata
#
#       async def get_by_es_id(self, es_id: str) -> LogMetadata | None:
#           """Cherche par ID Elasticsearch."""
#           pass
#
#       async def get_recent(self, limit: int = 100) -> list[LogMetadata]:
#           """Récupère les logs les plus récents."""
#           pass
#
#       async def get_stats_by_source(self, date_from, date_to) -> list[dict]:
#           """Statistiques par source de log."""
#           pass
#
#       async def delete_older_than(self, days: int) -> int:
#           """Purge les métadonnées plus vieilles que N jours."""
#           pass

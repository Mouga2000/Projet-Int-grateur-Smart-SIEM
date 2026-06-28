# app/repositories/playbook_repo.py
# -------------------------------
# Repository pour Playbook — index ES "playbooks"
#
# Ce que tu dois mettre ici :
#
#   from elasticsearch import AsyncElasticsearch
#   from typing import Optional, List
#   from app.core.config import settings
#
#   class PlaybookRepository:
#       """CRUD pour les playbooks SOAR dans Elasticsearch."""
#
#       def __init__(self, es: AsyncElasticsearch):
#           self.es = es
#           self.index = settings.ELASTICSEARCH_INDEX_PLAYBOOKS
#
#       async def create(self, playbook_data: dict) -> dict:
#           pass
#
#       async def get_by_id(self, playbook_id: str) -> Optional[dict]:
#           pass
#
#       async def get_enabled_playbooks(self) -> List[dict]:
#           """Playbooks actifs (déclenchés automatiquement)."""
#           pass
#
#       async def update(self, playbook_id: str, update_data: dict) -> bool:
#           pass
#
#       async def delete(self, playbook_id: str) -> bool:
#           pass
#
#       async def increment_execution(self, playbook_id: str):
#           """Incrémente le compteur d'exécution et met à jour last_executed_at."""
#           pass

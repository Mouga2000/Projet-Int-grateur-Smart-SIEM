# app/repositories/playbook_repo.py
# -------------------------------
# Repository pour Playbook
#
# Ce que tu dois mettre ici :
#
#   from app.repositories.base import BaseRepository
#   from app.models.playbook import Playbook
#
#   class PlaybookRepository(BaseRepository):
#       """CRUD pour les playbooks SOAR."""
#
#       def __init__(self, db):
#           super().__init__(db)
#           self.model = Playbook
#
#       async def get_enabled_playbooks(self) -> list[Playbook]:
#           pass
#
#       async def get_by_trigger(self, trigger: str) -> list[Playbook]:
#           """Récupère les playbooks déclenchés par un événement."""
#           pass
#
#       async def increment_execution_count(self, playbook_id: int):
#           """Incrémente le compteur d'exécution."""
#           pass

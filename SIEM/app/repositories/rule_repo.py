# app/repositories/rule_repo.py
# -------------------------------
# Repository pour Rule (règles de corrélation)
#
# Ce que tu dois mettre ici :
#
#   from app.repositories.base import BaseRepository
#   from app.models.rule import Rule
#
#   class RuleRepository(BaseRepository):
#       """CRUD pour les règles de corrélation."""
#
#       def __init__(self, db):
#           super().__init__(db)
#           self.model = Rule
#
#       async def get_enabled_rules(self) -> list[Rule]:
#           """Récupère toutes les règles actives."""
#           pass
#
#       async def get_by_type(self, rule_type: str) -> list[Rule]:
#           """Filtre par type de règle."""
#           pass
#
#       async def get_by_mitre_id(self, mitre_id: str) -> list[Rule]:
#           """Filtre par technique MITRE ATT&CK."""
#           pass

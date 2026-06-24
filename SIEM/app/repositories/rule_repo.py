# app/repositories/rule_repo.py
# -------------------------------
# Repository pour Rule — index ES "rules"
#
# Ce que tu dois mettre ici :
#
#   from elasticsearch import AsyncElasticsearch
#   from typing import Optional, List
#   from app.core.config import settings
#
#   class RuleRepository:
#       """CRUD pour les règles de corrélation dans Elasticsearch."""
#
#       def __init__(self, es: AsyncElasticsearch):
#           self.es = es
#           self.index = settings.ELASTICSEARCH_INDEX_RULES
#
#       async def create(self, rule_data: dict) -> dict:
#           pass
#
#       async def get_by_id(self, rule_id: str) -> Optional[dict]:
#           pass
#
#       async def get_enabled_rules(self) -> List[dict]:
#           """Récupère toutes les règles actives."""
#           pass
#
#       async def get_by_type(self, rule_type: str) -> List[dict]:
#           """Filtre par type de règle (threshold, correlation, ueba...)."""
#           pass
#
#       async def get_by_mitre_id(self, mitre_id: str) -> List[dict]:
#           """Filtre par technique MITRE ATT&CK."""
#           pass
#
#       async def update(self, rule_id: str, update_data: dict) -> bool:
#           pass
#
#       async def delete(self, rule_id: str) -> bool:
#           pass

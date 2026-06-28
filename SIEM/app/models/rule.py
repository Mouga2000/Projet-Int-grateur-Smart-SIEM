# app/models/rule.py
# -------------------------------
# Modèle Rule (règle de corrélation) — stocké dans l'index ES "rules"
#
# Ce que tu dois mettre ici :
#
#   from pydantic import BaseModel, Field
#   from typing import Optional, List
#   from datetime import datetime
#   from enum import Enum
#
#   class RuleType(str, Enum):
#       SINGLE_EVENT = "single_event"
#       THRESHOLD = "threshold"
#       CORRELATION = "correlation"
#       SEQUENCE = "sequence"
#       UEBA = "ueba"
#       CUSTOM = "custom"
#
#   class Rule(BaseModel):
#       """Règle de détection / corrélation d'événements."""
#       id: Optional[str] = None
#       name: str
#       description: Optional[str] = None
#       rule_type: RuleType
#       enabled: bool = True
#       severity: str = "medium"             # low, medium, high, critical
#       mitre_attack_id: Optional[str] = None
#       mitre_tactic: Optional[str] = None
#       sigma_rule: Optional[str] = None     # Règle au format Sigma (YAML)
#       condition: dict = {}                 # {"field": "event_type", "operator": "eq", "value": "login_failed", "threshold": 5, "window": "5m"}
#       actions: dict = {}                   # {"create_alert": True, "run_playbook": "playbook_id", "notify_slack": True}
#       priority: int = 50                   # 1-100
#       version: int = 1
#       created_by: Optional[str] = None
#       tags: List[str] = []
#       created_at: datetime = Field(default_factory=datetime.now)
#       updated_at: datetime = Field(default_factory=datetime.now)
#
#       def to_es_document(self) -> dict:
#           return self.model_dump(exclude={"id"})

# app/models/playbook.py
# -------------------------------
# Modèle Playbook SOAR — stocké dans l'index ES "playbooks"
#
# Ce que tu dois mettre ici :
#
#   from pydantic import BaseModel, Field
#   from typing import Optional, List
#   from datetime import datetime
#   from enum import Enum
#
#   class PlaybookTrigger(str, Enum):
#       MANUAL = "manual"
#       ALERT_CREATED = "alert_created"
#       ALERT_ESCALATED = "alert_escalated"
#       SCHEDULED = "scheduled"
#       WEBHOOK = "webhook"
#
#   class Playbook(BaseModel):
#       """Playbook d'automatisation SOAR."""
#       id: Optional[str] = None
#       name: str
#       description: Optional[str] = None
#       trigger: PlaybookTrigger = PlaybookTrigger.MANUAL
#       enabled: bool = True
#       steps: List[dict] = []               # [{"action": "enrich_ip", "params": {"ip": "{{source_ip}}", "provider": "virustotal"}}, ...]
#       variables: dict = {}
#       timeout_seconds: int = 300
#       max_retries: int = 3
#       last_executed_at: Optional[datetime] = None
#       execution_count: int = 0
#       created_by: Optional[str] = None
#       created_at: datetime = Field(default_factory=datetime.now)
#       updated_at: datetime = Field(default_factory=datetime.now)
#
#       def to_es_document(self) -> dict:
#           return self.model_dump(exclude={"id"})

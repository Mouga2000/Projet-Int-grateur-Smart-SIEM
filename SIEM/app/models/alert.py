# app/models/alert.py
# -------------------------------
# Modèle Alert — stocké dans l'index Elasticsearch "alerts"
#
# Ce que tu dois mettre ici :
#
#   from pydantic import BaseModel, Field
#   from typing import Optional, List
#   from datetime import datetime
#   from enum import Enum
#
#   class AlertSeverity(str, Enum):
#       LOW = "low"
#       MEDIUM = "medium"
#       HIGH = "high"
#       CRITICAL = "critical"
#
#   class AlertStatus(str, Enum):
#       OPEN = "open"
#       IN_PROGRESS = "in_progress"
#       RESOLVED = "resolved"
#       DISMISSED = "dismissed"
#
#   class Alert(BaseModel):
#       id: Optional[str] = None
#       title: str
#       description: Optional[str] = None
#       severity: AlertSeverity = AlertSeverity.MEDIUM
#       status: AlertStatus = AlertStatus.OPEN
#       source: str
#       rule_id: Optional[str] = None
#       rule_name: Optional[str] = None
#       mitre_attack_id: Optional[str] = None
#       log_ids: List[str] = []
#       score: Optional[float] = None
#       assigned_to: Optional[str] = None
#       created_at: datetime = Field(default_factory=datetime.now)
#       updated_at: datetime = Field(default_factory=datetime.now)
#       resolved_at: Optional[datetime] = None
#       resolution_notes: Optional[str] = None
#       escalated: bool = False
#
#       def to_es_document(self) -> dict:
#           return self.model_dump(exclude={"id"})

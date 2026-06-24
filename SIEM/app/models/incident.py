# app/models/incident.py
# -------------------------------
# Modèle Incident — stocké dans l'index ES "incidents"
#
# Ce que tu dois mettre ici :
#
#   from pydantic import BaseModel, Field
#   from typing import Optional, List
#   from datetime import datetime
#   from enum import Enum
#
#   class IncidentStatus(str, Enum):
#       NEW = "new"
#       INVESTIGATING = "investigating"
#       CONTAINED = "contained"
#       ERADICATED = "eradicated"
#       RECOVERED = "recovered"
#       CLOSED = "closed"
#
#   class IncidentSeverity(str, Enum):
#       LOW = "low"
#       MEDIUM = "medium"
#       HIGH = "high"
#       CRITICAL = "critical"
#
#   class Incident(BaseModel):
#       id: Optional[str] = None
#       title: str
#       description: Optional[str] = None
#       status: IncidentStatus = IncidentStatus.NEW
#       severity: IncidentSeverity = IncidentSeverity.MEDIUM
#       alert_ids: List[str] = []
#       rule_ids: List[str] = []
#       mitre_attack_ids: List[str] = []
#       affected_assets: List[str] = []
#       assigned_to: Optional[str] = None
#       created_at: datetime = Field(default_factory=datetime.now)
#       updated_at: datetime = Field(default_factory=datetime.now)
#       closed_at: Optional[datetime] = None
#       resolution_notes: Optional[str] = None
#       timeline: List[dict] = []
#
#       def to_es_document(self) -> dict:
#           return self.model_dump(exclude={"id"})

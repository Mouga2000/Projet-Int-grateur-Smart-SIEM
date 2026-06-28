# app/schemas/alert_schemas.py
# -------------------------------
# Schémas Pydantic pour les alertes et playbooks
#
# Ce que tu dois mettre ici :
#
#   from pydantic import BaseModel, Field
#   from datetime import datetime
#   from typing import Optional
#   from enum import Enum
#
#   # --- Alertes ---
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
#   class AlertUpdate(BaseModel):
#       status: Optional[AlertStatus] = None
#       assigned_to: Optional[int] = None
#       resolution_notes: Optional[str] = None
#
#   class AlertResponse(BaseModel):
#       id: int
#       title: str
#       description: Optional[str]
#       severity: AlertSeverity
#       status: AlertStatus
#       source: str
#       rule_id: Optional[int]
#       mitre_attack_id: Optional[str]
#       log_ids: list
#       score: Optional[float]
#       assigned_to: Optional[int]
#       created_at: datetime
#       resolved_at: Optional[datetime]
#
#   class AlertListResponse(BaseModel):
#       items: list[AlertResponse]
#       total: int
#       page: int
#       size: int
#
#   # --- Playbooks ---
#   class PlaybookCreate(BaseModel):
#       name: str
#       description: Optional[str] = None
#       trigger: str = "manual"
#       steps: list = []
#       variables: dict = {}
#
#   class PlaybookUpdate(BaseModel):
#       name: Optional[str] = None
#       description: Optional[str] = None
#       enabled: Optional[bool] = None
#       steps: Optional[list] = None
#
#   class PlaybookResponse(BaseModel):
#       id: int
#       name: str
#       description: Optional[str]
#       trigger: str
#       enabled: bool
#       steps: list
#       variables: dict
#       last_executed_at: Optional[datetime]
#       execution_count: int
#       created_at: datetime

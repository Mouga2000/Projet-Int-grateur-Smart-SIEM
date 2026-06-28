# app/models/log.py
# -------------------------------
# Modèle Log — stocké dans l'index Elasticsearch "logs-YYYY-MM-DD"
#
# Ce que tu dois mettre ici :
#
#   from pydantic import BaseModel, Field
#   from typing import Optional, List, Any
#   from datetime import datetime
#
#   class Log(BaseModel):
#       """Log de sécurité normalisé."""
#       id: Optional[str] = None
#       timestamp: datetime
#       received_at: datetime = Field(default_factory=datetime.now)
#       source: str                # syslog, windows_event, netflow, api
#       source_host: Optional[str] = None
#       source_ip: Optional[str] = None
#       log_type: Optional[str] = None
#       severity: str = "info"     # debug, info, warning, error, critical
#       message: str
#       raw_data: Optional[dict] = None
#       tags: List[str] = []
#       event_code: Optional[str] = None
#       process: Optional[dict] = None
#       user: Optional[dict] = None
#       network: Optional[dict] = None
#       file: Optional[dict] = None
#       registry: Optional[dict] = None
#       mitre_attack_id: Optional[str] = None
#
#       def to_es_document(self) -> dict:
#           return self.model_dump(exclude={"id"})

# app/schemas/log_schemas.py
# -------------------------------
# Schémas Pydantic pour les logs
#
# Ce que tu dois mettre ici :
#
#   from pydantic import BaseModel, Field
#   from datetime import datetime
#   from typing import Optional, Any
#
#   class LogCreate(BaseModel):
#       """Schéma d'ingestion d'un log."""
#       timestamp: datetime
#       source: str  # syslog, windows_event, netflow, api, custom
#       source_host: Optional[str] = None
#       log_type: Optional[str] = None
#       severity: Optional[str] = "info"
#       message: str
#       raw_data: Optional[dict] = None
#       tags: list[str] = []
#
#   class LogResponse(BaseModel):
#       id: str
#       timestamp: datetime
#       source: str
#       source_host: Optional[str] = None
#       log_type: Optional[str] = None
#       severity: str
#       message: str
#       tags: list[str]
#
#   class LogListResponse(BaseModel):
#       items: list[LogResponse]
#       total: int
#       page: int
#       size: int
#       pages: int

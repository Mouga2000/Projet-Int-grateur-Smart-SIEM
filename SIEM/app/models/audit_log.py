# app/models/audit_log.py
# -------------------------------
# Modèle AuditLog — stocké dans l'index ES "audit-YYYY-MM-DD"
#
# Ce que tu dois mettre ici :
#
#   from pydantic import BaseModel, Field
#   from typing import Optional
#   from datetime import datetime
#
#   class AuditLog(BaseModel):
#       """Trace d'une action sensible dans le SIEM."""
#       id: Optional[str] = None
#       user_id: str = "system"
#       username: Optional[str] = None
#       action: str                          # login, logout, mfa_verify, create_user, update_role, delete_user...
#       result: str = "success"              # success, failed
#       resource_type: Optional[str] = None
#       resource_id: Optional[str] = None
#       details: dict = {}
#       ip_address: str = "unknown"
#       timestamp: datetime = Field(default_factory=datetime.now)
#
#       def to_es_document(self) -> dict:
#           return self.model_dump(exclude={"id"})

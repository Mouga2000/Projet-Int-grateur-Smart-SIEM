# app/schemas/alert_schemas.py
# -------------------------------
# Schemas Pydantic pour les alertes

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AlertResponse(BaseModel):
    id: int
    rule_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    severity: str
    source_ip: Optional[str] = None
    host: Optional[str] = None
    status: str
    confidence: int = 50
    mitre: dict = {}
    created_at: Optional[datetime] = None


class AlertUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(ouverte|en_cours|resolue|classee)$")
    confidence: Optional[int] = Field(None, ge=0, le=100)


class AlertListResponse(BaseModel):
    items: List[AlertResponse]
    total: int
    page: int
    size: int
    pages: int

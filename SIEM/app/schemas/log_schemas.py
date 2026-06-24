# app/schemas/log_schemas.py
# -------------------------------
# Schémas Pydantic pour les logs

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class RawLog(BaseModel):
    """Schéma tolérant : accepte n'importe quel JSON.
    La normalisation extraira les champs utiles et comblera les absents."""
    timestamp: Optional[datetime] = None
    source_ip: Optional[str] = None
    host: Optional[str] = None
    log_type: Optional[str] = None
    severity: Optional[str] = None
    raw_message: Optional[str] = None
    message: Optional[str] = None          # Alternative à raw_message
    raw_data: Optional[dict] = None

class LogCreate(BaseModel):
    """Schéma strict d'ingestion (pour usage interne ou tests)."""
    timestamp: datetime
    source_ip: str = Field(..., description="Adresse IP source de l'événement")
    host: str = Field(..., description="Nom de la machine source")
    log_type: Optional[str] = None
    severity: str = Field(default="info", pattern="^(debug|info|warning|error|critical)$")
    raw_message: str = Field(..., description="Message brut du log")
    raw_data: Optional[dict] = None

class LogResponse(BaseModel):
    """Schéma de réponse après ingestion d'un log normalisé."""
    id: str
    timestamp: datetime
    source_ip: str
    host: str
    log_type: Optional[str] = None
    severity: str
    raw_message: str
    tags: List[str] = []

class LogListResponse(BaseModel):
    """Liste paginée de logs."""
    items: List[LogResponse]
    total: int
    page: int
    size: int
    pages: int

class LogSearchRequest(BaseModel):
    """Requête de recherche avancée."""
    query: str = "*"
    source_ips: List[str] = []
    severities: List[str] = []
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=50, ge=1, le=1000)

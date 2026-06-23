# app/models/user.py
# -------------------------------
# Modèle User — Utilisateurs de la plateforme SIEM
#
# Ce que tu dois mettre ici :
#
#   from sqlalchemy import String, Boolean, DateTime, Enum as SAEnum
#   from sqlalchemy.orm import Mapped, mapped_column
#   from app.models.base import Base, TimestampMixin, SoftDeleteMixin
#   import enum
#
#   class UserRole(enum.Enum):
#       ADMIN = "admin"
#       ANALYST = "analyst"
#       VIEWER = "viewer"
#       AUTOMATION = "automation"  # Compte API / service
#
#   class User(Base, TimestampMixin, SoftDeleteMixin):
#       __tablename__ = "users"
#
#       id: Mapped[int] = mapped_column(primary_key=True)
#       email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
#       username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
#       hashed_password: Mapped[str] = mapped_column(String(255))
#       full_name: Mapped[str | None] = mapped_column(String(255))
#       role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.VIEWER)
#       is_active: Mapped[bool] = mapped_column(Boolean, default=True)
#       is_mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
#       mfa_secret: Mapped[str | None] = mapped_column(String(64))  # Clé secrète TOTP
#       last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
#
#   # Index : ix_users_email, ix_users_username
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    id: Optional[str] = None
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password_hash: str
    mfa_secret: Optional[str] = None
    mfa_enabled: bool = False
    role: str  # "lecteur", "analyste", "rssi", "administrateur"
    perimeter: List[str] = []  # ["equipe_reseau", "service_prod", ...]
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    is_active: bool = True
    
    def to_es_document(self) -> dict:
        """Convertit le modèle en document Elasticsearch"""
        return self.model_dump(exclude={"id"})
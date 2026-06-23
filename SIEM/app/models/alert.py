# app/models/alert.py
# -------------------------------
# Modèle Alert — Représente une alerte générée par les règles de corrélation
#
# Ce que tu dois mettre ici :
#
#   from sqlalchemy import String, Integer, Float, DateTime, JSON, Text, ForeignKey, Enum as SAEnum
#   from sqlalchemy.orm import Mapped, mapped_column, relationship
#   from app.models.base import Base, TimestampMixin, SoftDeleteMixin
#   import enum
#   from datetime import datetime
#
#   class AlertSeverity(enum.Enum):
#       LOW = "low"
#       MEDIUM = "medium"
#       HIGH = "high"
#       CRITICAL = "critical"
#
#   class AlertStatus(enum.Enum):
#       OPEN = "open"
#       IN_PROGRESS = "in_progress"
#       RESOLVED = "resolved"
#       DISMISSED = "dismissed"
#
#   class Alert(Base, TimestampMixin, SoftDeleteMixin):
#       __tablename__ = "alerts"
#
#       id: Mapped[int] = mapped_column(primary_key=True)
#       title: Mapped[str] = mapped_column(String(255))
#       description: Mapped[str | None] = mapped_column(Text)
#       severity: Mapped[AlertSeverity] = mapped_column(SAEnum(AlertSeverity), default=AlertSeverity.MEDIUM)
#       status: Mapped[AlertStatus] = mapped_column(SAEnum(AlertStatus), default=AlertStatus.OPEN)
#       source: Mapped[str] = mapped_column(String(100))  # correlation | rule | manual
#       rule_id: Mapped[int | None] = mapped_column(ForeignKey("rules.id"))
#       mitre_attack_id: Mapped[str | None] = mapped_column(String(20))  # ex: T1059
#       log_ids: Mapped[list] = mapped_column(JSON, default=list)  # IDs Elasticsearch associés
#       context: Mapped[dict] = mapped_column(JSON, default=dict)  # Contexte enrichi
#       score: Mapped[float | None] = mapped_column(Float)  # Score de criticité (0-100)
#       assigned_to: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
#       resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
#       resolution_notes: Mapped[str | None] = mapped_column(Text)
#
#       # Relations
#       assignee = relationship("User", foreign_keys=[assigned_to])
#       rule = relationship("Rule", foreign_keys=[rule_id])

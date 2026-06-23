# app/models/incident.py
# -------------------------------
# Modèle Incident — Regroupement d'alertes liées à une même menace
#
# Ce que tu dois mettre ici :
#
#   from sqlalchemy import String, Integer, DateTime, JSON, Text, ForeignKey, Enum as SAEnum
#   from sqlalchemy.orm import Mapped, mapped_column, relationship
#   from app.models.base import Base, TimestampMixin, SoftDeleteMixin
#   import enum
#   from datetime import datetime
#
#   class IncidentStatus(enum.Enum):
#       NEW = "new"
#       INVESTIGATING = "investigating"
#       CONTAINED = "contained"
#       ERADICATED = "eradicated"
#       RECOVERED = "recovered"
#       CLOSED = "closed"
#
#   class IncidentSeverity(enum.Enum):
#       LOW = "low"
#       MEDIUM = "medium"
#       HIGH = "high"
#       CRITICAL = "critical"
#
#   class Incident(Base, TimestampMixin, SoftDeleteMixin):
#       __tablename__ = "incidents"
#
#       id: Mapped[int] = mapped_column(primary_key=True)
#       title: Mapped[str] = mapped_column(String(255))
#       description: Mapped[str | None] = mapped_column(Text)
#       status: Mapped[IncidentStatus] = mapped_column(SAEnum(IncidentStatus), default=IncidentStatus.NEW)
#       severity: Mapped[IncidentSeverity] = mapped_column(SAEnum(IncidentSeverity), default=IncidentSeverity.MEDIUM)
#       alert_ids: Mapped[list] = mapped_column(JSON, default=list)  # IDs des alertes liées
#       mitre_attack_ids: Mapped[list] = mapped_column(JSON, default=list)  # Tactiques MITRE
#       affected_assets: Mapped[list] = mapped_column(JSON, default=list)  # Hôtes/IPs affectés
#       lead_investigator: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
#       containment_strategy: Mapped[str | None] = mapped_column(Text)
#       remediation_steps: Mapped[list] = mapped_column(JSON, default=list)
#       lessons_learned: Mapped[str | None] = mapped_column(Text)
#       closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
#
#       lead = relationship("User", foreign_keys=[lead_investigator])

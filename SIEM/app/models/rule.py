# app/models/rule.py
# -------------------------------
# Modèle Rule — Règles de corrélation / détection
#
# Ce que tu dois mettre ici :
#
#   from sqlalchemy import String, Integer, Boolean, DateTime, JSON, Text, Enum as SAEnum
#   from sqlalchemy.orm import Mapped, mapped_column
#   from app.models.base import Base, TimestampMixin, SoftDeleteMixin
#   import enum
#
#   class RuleType(enum.Enum):
#       SINGLE_EVENT = "single_event"       # Événement unique détecté
#       THRESHOLD = "threshold"              # Seuil dépassé sur une fenêtre
#       CORRELATION = "correlation"          # Corrélation multi-sources
#       SEQUENCE = "sequence"                # Séquence d'événements
#       UEBA = "ueba"                        # Anomalie comportementale
#       CUSTOM = "custom"                    # Règle personnalisée (Sigma)
#
#   class Rule(Base, TimestampMixin, SoftDeleteMixin):
#       __tablename__ = "rules"
#
#       id: Mapped[int] = mapped_column(primary_key=True)
#       name: Mapped[str] = mapped_column(String(255), index=True)
#       description: Mapped[str | None] = mapped_column(Text)
#       rule_type: Mapped[RuleType] = mapped_column(SAEnum(RuleType))
#       enabled: Mapped[bool] = mapped_column(Boolean, default=True)
#       severity: Mapped[str] = mapped_column(String(20), default="medium")  # low/medium/high/critical
#       mitre_attack_id: Mapped[str | None] = mapped_column(String(20))
#       sigma_rule: Mapped[str | None] = mapped_column(Text)  # Format Sigma si applicable
#       condition: Mapped[dict] = mapped_column(JSON, default=dict)
#       # condition stocke : {"field": "event_type", "operator": "eq", "value": "login_failed", "threshold": 5, "window": "5m"}
#       actions: Mapped[dict] = mapped_column(JSON, default=dict)
#       # actions stocke : {"create_alert": true, "run_playbook": 1, "notify_slack": true}
#       priority: Mapped[int] = mapped_column(Integer, default=50)  # 1-100
#       version: Mapped[int] = mapped_column(Integer, default=1)
#
#   # Unicité : (name) doit être unique sauf soft-deleted

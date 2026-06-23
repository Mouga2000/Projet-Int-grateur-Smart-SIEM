# app/models/playbook.py
# -------------------------------
# Modèle Playbook — Automatisation SOAR
#
# Ce que tu dois mettre ici :
#
#   from sqlalchemy import String, Integer, Boolean, JSON, Text, Enum as SAEnum
#   from sqlalchemy.orm import Mapped, mapped_column
#   from app.models.base import Base, TimestampMixin, SoftDeleteMixin
#   import enum
#
#   class PlaybookTrigger(enum.Enum):
#       MANUAL = "manual"
#       ALERT_CREATED = "alert_created"
#       ALERT_ESCALATED = "alert_escalated"
#       SCHEDULED = "scheduled"
#       WEBHOOK = "webhook"
#
#   class Playbook(Base, TimestampMixin, SoftDeleteMixin):
#       __tablename__ = "playbooks"
#
#       id: Mapped[int] = mapped_column(primary_key=True)
#       name: Mapped[str] = mapped_column(String(255))
#       description: Mapped[str | None] = mapped_column(Text)
#       trigger: Mapped[PlaybookTrigger] = mapped_column(SAEnum(PlaybookTrigger), default=PlaybookTrigger.MANUAL)
#       enabled: Mapped[bool] = mapped_column(Boolean, default=True)
#       steps: Mapped[list] = mapped_column(JSON, default=list)
#       # steps : [{"action": "enrich_ip", "params": {"ip": "{{source_ip}}", "provider": "virustotal"}}, ...]
#       # Actions possibles : enrich_ip, enrich_domain, block_ip, isolate_host, notify_slack, notify_email, create_ticket, run_script
#       variables: Mapped[dict] = mapped_column(JSON, default=dict)
#       timeout_seconds: Mapped[int] = mapped_column(Integer, default=300)
#       max_retries: Mapped[int] = mapped_column(Integer, default=3)
#       last_executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
#       execution_count: Mapped[int] = mapped_column(Integer, default=0)

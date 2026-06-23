# app/models/audit_log.py
# -------------------------------
# Modèle AuditLog — Trace de toutes les actions sensibles
#
# Ce que tu dois mettre ici :
#
#   from sqlalchemy import String, Integer, DateTime, JSON, Text
#   from sqlalchemy.orm import Mapped, mapped_column
#   from app.models.base import Base, TimestampMixin
#   from datetime import datetime
#
#   class AuditLog(Base, TimestampMixin):
#       __tablename__ = "audit_logs"
#
#       id: Mapped[int] = mapped_column(primary_key=True)
#       user_id: Mapped[int | None] = mapped_column(Integer, index=True)
#       action: Mapped[str] = mapped_column(String(100), index=True)
#       # Exemples d'action : "user.login", "alert.update", "rule.create", "playbook.execute"
#       resource_type: Mapped[str | None] = mapped_column(String(100))
#       resource_id: Mapped[str | None] = mapped_column(String(100))
#       details: Mapped[dict] = mapped_column(JSON, default=dict)  # Payload de l'action
#       ip_address: Mapped[str | None] = mapped_column(String(45))
#       user_agent: Mapped[str | None] = mapped_column(String(500))
#       success: Mapped[bool] = mapped_column(default=True)
#
#   # Index composite : (user_id, action, created_at)

# app/models/notification.py
# -------------------------------
# Modèle Notification — Notifications destinées aux utilisateurs
#
# Ce que tu dois mettre ici :
#
#   from sqlalchemy import String, Integer, Boolean, DateTime, JSON, Text, ForeignKey, Enum as SAEnum
#   from sqlalchemy.orm import Mapped, mapped_column
#   from app.models.base import Base, TimestampMixin
#   import enum
#   from datetime import datetime
#
#   class NotificationChannel(enum.Enum):
#       IN_APP = "in_app"
#       EMAIL = "email"
#       SLACK = "slack"
#       SMS = "sms"
#
#   class Notification(Base, TimestampMixin):
#       __tablename__ = "notifications"
#
#       id: Mapped[int] = mapped_column(primary_key=True)
#       user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
#       title: Mapped[str] = mapped_column(String(255))
#       message: Mapped[str] = mapped_column(Text)
#       channel: Mapped[NotificationChannel] = mapped_column(SAEnum(NotificationChannel), default=NotificationChannel.IN_APP)
#       is_read: Mapped[bool] = mapped_column(Boolean, default=False)
#       read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
#       reference_type: Mapped[str | None] = mapped_column(String(50))  # alert | incident | report
#       reference_id: Mapped[str | None] = mapped_column(String(50))
#       delivered: Mapped[bool] = mapped_column(Boolean, default=False)
#       delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

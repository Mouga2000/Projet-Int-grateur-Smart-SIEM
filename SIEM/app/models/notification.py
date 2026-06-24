# app/models/notification.py
# -------------------------------
# Modèle Notification — stocké dans l'index ES "notifications"
#
# Ce que tu dois mettre ici :
#
#   from pydantic import BaseModel, Field
#   from typing import Optional
#   from datetime import datetime
#   from enum import Enum
#
#   class NotificationChannel(str, Enum):
#       IN_APP = "in_app"
#       EMAIL = "email"
#       SLACK = "slack"
#       SMS = "sms"
#
#   class Notification(BaseModel):
#       """Notification destinée à un utilisateur."""
#       id: Optional[str] = None
#       user_id: str
#       title: str
#       message: str
#       channel: NotificationChannel = NotificationChannel.IN_APP
#       is_read: bool = False
#       read_at: Optional[datetime] = None
#       reference_type: Optional[str] = None  # alert, incident, report
#       reference_id: Optional[str] = None
#       delivered: bool = False
#       delivered_at: Optional[datetime] = None
#       created_at: datetime = Field(default_factory=datetime.now)
#
#       def to_es_document(self) -> dict:
#           return self.model_dump(exclude={"id"})

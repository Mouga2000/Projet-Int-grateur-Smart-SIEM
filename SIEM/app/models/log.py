# app/models/log.py
# -------------------------------
# Modèle Log (table PostgreSQL pour les métadonnées des logs)
#
# NOTE : Les logs bruts sont stockés dans Elasticsearch.
#        Ce modèle stocke les métadonnées/références en PostgreSQL.
#
# Ce que tu dois mettre ici :
#
#   from sqlalchemy import String, Integer, DateTime, JSON, Text, Enum as SAEnum
#   from sqlalchemy.orm import Mapped, mapped_column
#   from app.models.base import Base, TimestampMixin
#   import enum
#
#   class LogSource(enum.Enum):
#       SYSLOG = "syslog"
#       WINDOWS_EVENT = "windows_event"
#       NETFLOW = "netflow"
#       API = "api"
#       CUSTOM = "custom"
#
#   class LogMetadata(Base, TimestampMixin):
#       __tablename__ = "log_metadata"
#
#       id: Mapped[int] = mapped_column(primary_key=True)
#       es_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)  # ID dans Elasticsearch
#       source: Mapped[LogSource] = mapped_column(SAEnum(LogSource))
#       source_host: Mapped[str | None] = mapped_column(String(255))
#       log_type: Mapped[str | None] = mapped_column(String(100))
#       severity: Mapped[str | None] = mapped_column(String(50))
#       timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
#       received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
#       tags: Mapped[dict] = mapped_column(JSON, default=dict)
#       raw_size: Mapped[int | None] = mapped_column(Integer)
#       hash: Mapped[str | None] = mapped_column(String(64))  # SHA256 pour déduplication

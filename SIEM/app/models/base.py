# app/models/base.py
# -------------------------------
# Base déclarative SQLAlchemy et mixins partagés
#
# Ce que tu dois mettre ici :
#
#   from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
#   from sqlalchemy import DateTime, func
#   from datetime import datetime
#
#   class Base(DeclarativeBase):
#       """Base déclarative pour tous les modèles."""
#       pass
#
#   class TimestampMixin:
#       """Ajoute les colonnes created_at et updated_at."""
#       created_at: Mapped[datetime] = mapped_column(
#           DateTime(timezone=True), server_default=func.now()
#       )
#       updated_at: Mapped[datetime] = mapped_column(
#           DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
#       )
#
#   class SoftDeleteMixin:
#       """Ajoute une colonne deleted_at pour le soft-delete."""
#       deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

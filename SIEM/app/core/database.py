# app/core/database.py
# -------------------------------
# Connexion PostgreSQL asynchrone avec SQLAlchemy
#
# Ce que tu dois mettre ici :
#
#   from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
#   from app.core.config import settings
#
#   # Moteur asynchrone
#   engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, pool_size=20, max_overflow=10)
#
#   # Factory de sessions
#   async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
#
#   # Dépendance FastAPI pour obtenir une session
#   async def get_db() -> AsyncSession:
#       async with async_session_factory() as session:
#           try:
#               yield session
#               await session.commit()
#           except Exception:
#               await session.rollback()
#               raise
#
#   # Initialisation / création des tables (optionnel, Alembic est recommandé)
#   async def init_db():
#       from app.models.base import Base
#       async with engine.begin() as conn:
#           await conn.run_sync(Base.metadata.create_all)

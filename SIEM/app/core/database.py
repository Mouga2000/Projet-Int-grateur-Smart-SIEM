# app/core/database.py
# -------------------------------
# Connexion PostgreSQL avec SQLAlchemy 2.0 asynchrone (asyncpg)
#
# Les données relationnelles (utilisateurs, règles, audits…) sont stockées ici.
# Les logs et données volumineuses restent dans Elasticsearch.

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
from app.models.sql_models import Base

# Moteur asynchrone PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=5,
    pool_timeout=30,
)

# Factory de sessions asynchrones
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """Dépendance FastAPI : injecte une session PostgreSQL."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Crée toutes les tables PostgreSQL si elles n'existent pas."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Ferme la connexion à la base de données."""
    await engine.dispose()

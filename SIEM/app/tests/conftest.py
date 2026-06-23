# app/tests/conftest.py
# -------------------------------
# Configuration des fixtures pytest pour les tests
#
# Ce que tu dois mettre ici :
#
#   import pytest
#   from httpx import AsyncClient, ASGITransport
#   from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
#   from app.main import app
#   from app.core.database import get_db
#   from app.models.base import Base
#
#   # Utiliser une base de données SQLite en mémoire pour les tests
#   TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
#
#   @pytest.fixture(scope="session")
#   async def engine():
#       """Crée un moteur de test et les tables."""
#       engine = create_async_engine(TEST_DATABASE_URL, echo=False)
#       async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#       yield engine
#       async with engine.begin() as conn:
#           await conn.run_sync(Base.metadata.drop_all)
#
#   @pytest.fixture
#   async def db_session(engine):
#       """Fixture pour une session de test isolée."""
#       async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
#       async with async_session() as session:
#           yield session
#
#   @pytest.fixture
#   async def client(db_session):
#       """Fixture pour le client HTTP de test."""
#       async def override_get_db():
#           yield db_session
#       app.dependency_overrides[get_db] = override_get_db
#       async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
#           yield ac
#       app.dependency_overrides.clear()
#
#   @pytest.fixture
#   async def test_user(db_session):
#       """Crée un utilisateur de test."""
#       pass
#
#   @pytest.fixture
#   async def admin_user(db_session):
#       """Crée un utilisateur admin de test."""
#       pass
#
#   @pytest.fixture
#   async def auth_headers(test_user):
#       """Génère les headers d'authentification pour les tests."""
#       pass

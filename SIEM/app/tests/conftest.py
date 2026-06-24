# app/tests/conftest.py
# -------------------------------
# Configuration des fixtures pytest pour les tests
#
# Ce que tu dois mettre ici :
#
#   import pytest
#   from httpx import AsyncClient, ASGITransport
#   from app.main import app
#   from app.core.elasticsearch import get_es, ElasticsearchClient
#   from app.repositories.user_repo import UserRepository
#   from app.core.security import hash_password
#
#   @pytest.fixture(scope="session")
#   def es_client():
#       """Connexion Elasticsearch pour les tests."""
#       pass
#
#   @pytest.fixture
#   async def clean_index(es_client):
#       """Nettoie les index de test après chaque test."""
#       pass
#
#   @pytest.fixture
#   async def client():
#       """Client HTTP de test."""
#       async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
#           yield ac
#
#   @pytest.fixture
#   async def test_user(es_client):
#       """Crée un utilisateur de test dans ES."""
#       pass
#
#   @pytest.fixture
#   async def auth_headers(test_user):
#       """Génère les headers d'authentification JWT."""
#       pass

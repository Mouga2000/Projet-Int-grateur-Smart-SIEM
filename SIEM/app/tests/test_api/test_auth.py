# app/tests/test_api/test_auth.py
# -------------------------------
# Tests pour les endpoints /api/v1/auth
#
# Ce que tu dois tester ici :
#
#   import pytest
#   from httpx import AsyncClient
#
#   @pytest.mark.asyncio
#   async def test_login_success(client: AsyncClient, test_user):
#       """Test de connexion réussie."""
#       pass
#
#   @pytest.mark.asyncio
#   async def test_login_invalid_password(client: AsyncClient):
#       """Test de connexion avec mauvais mot de passe."""
#       pass
#
#   @pytest.mark.asyncio
#   async def test_login_inactive_user(client: AsyncClient):
#       """Test de connexion d'un utilisateur désactivé."""
#       pass
#
#   @pytest.mark.asyncio
#   async def test_refresh_token(client: AsyncClient, auth_headers):
#       """Test de rafraîchissement du token."""
#       pass
#
#   @pytest.mark.asyncio
#   async def test_logout(client: AsyncClient, auth_headers):
#       """Test de déconnexion (révocation du token)."""
#       pass
#
#   @pytest.mark.asyncio
#   async def test_get_me(client: AsyncClient, auth_headers):
#       """Test de récupération du profil."""
#       pass
#
#   @pytest.mark.asyncio
#   async def test_access_without_token(client: AsyncClient):
#       """Test d'accès sans token (401 attendu)."""
#       response = await client.get("/api/v1/users/me")
#       assert response.status_code == 401

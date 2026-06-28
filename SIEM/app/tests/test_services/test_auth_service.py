# app/tests/test_services/test_auth_service.py
# -------------------------------
# Tests unitaires du service d'authentification

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.auth import AuthService


@pytest.fixture
def mock_user_repo():
    repo = MagicMock()
    repo.get_user_by_username = AsyncMock()
    repo.update_last_login = AsyncMock()
    return repo


@pytest.fixture
def mock_audit_repo():
    repo = MagicMock()
    repo.log_login_attempt = AsyncMock()
    repo.log_logout = AsyncMock()
    return repo


@pytest.fixture
def auth_service(mock_user_repo, mock_audit_repo):
    return AuthService(mock_user_repo, mock_audit_repo)


class TestAuthenticateUser:

    @pytest.mark.asyncio
    async def test_authenticate_success(self, auth_service, mock_user_repo):
        mock_user_repo.get_user_by_username.return_value = {
            "id": 1,
            "username": "admin",
            "email": "admin@siem.local",
            "password_hash": "$2b$12$abcdefghijklmnopqrstuvwxyz12345678901234567890",
            "role": "administrateur",
            "perimeter": [],
            "mfa_enabled": False,
            "is_active": True,
        }
        # Need to mock verify_password to return True
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr("app.services.auth.verify_password", lambda p, h: True)
            result = await auth_service.authenticate_user("admin", "password123")

        assert "access_token" in result
        assert result["user"]["role"] == "administrateur"

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, auth_service, mock_user_repo):
        mock_user_repo.get_user_by_username.return_value = None

        with pytest.raises(Exception) as exc:
            await auth_service.authenticate_user("inconnu", "password")
        assert "401" in str(exc.value) or "Unauthorized" in str(exc.value)

    @pytest.mark.asyncio
    async def test_logout_logs_action(self, auth_service, mock_audit_repo):
        await auth_service.logout(1, "admin")
        mock_audit_repo.log_logout.assert_called_once_with(1, "admin")

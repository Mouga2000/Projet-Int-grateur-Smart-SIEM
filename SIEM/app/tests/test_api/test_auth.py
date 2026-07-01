# app/tests/test_api/test_auth.py
# -------------------------------
# Tests unitaires du service AuthService (mocké)

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.auth import AuthService


@pytest.fixture
def mock_user_repo():
    repo = MagicMock()
    repo.get_user_by_username = AsyncMock()
    repo.update_last_login = AsyncMock()
    repo.update_user = AsyncMock()
    return repo


@pytest.fixture
def mock_audit_repo():
    repo = MagicMock()
    repo.log_login_attempt = AsyncMock()
    repo.log_logout = AsyncMock()
    repo.log_mfa_verification = AsyncMock()
    return repo


@pytest.fixture
def auth_service(mock_user_repo, mock_audit_repo):
    return AuthService(mock_user_repo, mock_audit_repo)


@pytest.fixture
def active_user():
    return {
        "id": 1,
        "username": "admin",
        "email": "admin@siem.local",
        "password_hash": "$2b$12$hashed_password",
        "role": "administrateur",
        "perimeter": [],
        "mfa_enabled": False,
        "mfa_secret": None,
        "is_active": True,
    }


class TestAuthenticateUser:
    @pytest.mark.asyncio
    async def test_login_success_returns_tokens(
        self, auth_service, mock_user_repo, active_user
    ):
        mock_user_repo.get_user_by_username.return_value = active_user
        with patch("app.services.auth.verify_password", return_value=True):
            result = await auth_service.authenticate_user("admin", "password123")

        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"
        assert result["user"]["username"] == "admin"
        assert result["user"]["role"] == "administrateur"

    @pytest.mark.asyncio
    async def test_login_invalid_password_raises_error(
        self, auth_service, mock_user_repo, active_user
    ):
        mock_user_repo.get_user_by_username.return_value = active_user
        with patch("app.services.auth.verify_password", return_value=False):
            with pytest.raises(Exception) as exc:
                await auth_service.authenticate_user("admin", "wrongpassword")
            assert "401" in str(exc.value)

    @pytest.mark.asyncio
    async def test_login_user_not_found_raises_error(
        self, auth_service, mock_user_repo
    ):
        mock_user_repo.get_user_by_username.return_value = None
        with pytest.raises(Exception) as exc:
            await auth_service.authenticate_user("unknown", "password")
        assert "401" in str(exc.value)

    @pytest.mark.asyncio
    async def test_login_inactive_user_raises_error(self, auth_service, mock_user_repo):
        user = {
            "id": 2,
            "username": "disabled",
            "password_hash": "hash",
            "is_active": False,
            "mfa_enabled": False,
            "role": "lecteur",
        }
        mock_user_repo.get_user_by_username.return_value = user
        with patch("app.services.auth.verify_password", return_value=True):
            with pytest.raises(Exception) as exc:
                await auth_service.authenticate_user("disabled", "password")
            assert "403" in str(exc.value)

    @pytest.mark.asyncio
    async def test_login_with_mfa_required(self, auth_service, mock_user_repo):
        user = {
            "id": 3,
            "username": "mfa_user",
            "password_hash": "hash",
            "is_active": True,
            "mfa_enabled": True,
            "mfa_secret": "secret",
            "role": "analyste",
            "perimeter": [],
        }
        mock_user_repo.get_user_by_username.return_value = user
        with patch("app.services.auth.verify_password", return_value=True):
            with pytest.raises(Exception) as exc:
                await auth_service.authenticate_user("mfa_user", "password")
            assert "MFA" in str(exc.value)

    @pytest.mark.asyncio
    async def test_login_with_mfa_code_invalid(self, auth_service, mock_user_repo):
        user = {
            "id": 3,
            "username": "mfa_user",
            "password_hash": "hash",
            "is_active": True,
            "mfa_enabled": True,
            "mfa_secret": "secret",
            "role": "analyste",
            "perimeter": [],
        }
        mock_user_repo.get_user_by_username.return_value = user
        with patch("app.services.auth.verify_password", return_value=True):
            with patch("app.services.auth.verify_mfa", return_value=False):
                with pytest.raises(Exception) as exc:
                    await auth_service.authenticate_user(
                        "mfa_user", "password", mfa_code="000000"
                    )
                assert "MFA" in str(exc.value)

    @pytest.mark.asyncio
    async def test_login_with_valid_mfa_succeeds(self, auth_service, mock_user_repo):
        user = {
            "id": 3,
            "username": "mfa_user",
            "password_hash": "hash",
            "is_active": True,
            "mfa_enabled": True,
            "mfa_secret": "secret",
            "role": "analyste",
            "perimeter": [],
            "email": "mfa@siem.local",
        }
        mock_user_repo.get_user_by_username.return_value = user
        with patch("app.services.auth.verify_password", return_value=True):
            with patch("app.services.auth.verify_mfa", return_value=True):
                result = await auth_service.authenticate_user(
                    "mfa_user", "password", mfa_code="123456"
                )
                assert "access_token" in result

    @pytest.mark.asyncio
    async def test_logout_logs_action(self, auth_service, mock_audit_repo):
        await auth_service.logout(1, "admin")
        mock_audit_repo.log_logout.assert_called_once_with(1, "admin")

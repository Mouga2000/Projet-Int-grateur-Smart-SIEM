# app/tests/test_services/test_audit_service.py
# -------------------------------
# Tests unitaires du service d'audit (app/services/audit_service.py)

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.audit_service import AuditService, get_audit_service


@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.log_login_attempt = AsyncMock(return_value={"_id": 1})
    repo.log_logout = AsyncMock(return_value={"_id": 2})
    repo.log_mfa_verification = AsyncMock(return_value={"_id": 3})
    repo.log_user_management = AsyncMock(return_value={"_id": 4})
    return repo


@pytest.fixture
def service(mock_repo):
    return AuditService(mock_repo)


class TestAuditService:
    @pytest.mark.asyncio
    async def test_log_login(self, service, mock_repo):
        result = await service.log_login("1", "admin", True, "10.0.0.1")
        assert result["_id"] == 1
        mock_repo.log_login_attempt.assert_called_once_with("1", "admin", True, "10.0.0.1")

    @pytest.mark.asyncio
    async def test_log_login_failed(self, service, mock_repo):
        result = await service.log_login("1", "admin", False, "10.0.0.5")
        mock_repo.log_login_attempt.assert_called_once_with("1", "admin", False, "10.0.0.5")

    @pytest.mark.asyncio
    async def test_log_logout(self, service, mock_repo):
        result = await service.log_logout("1", "admin")
        assert result["_id"] == 2
        mock_repo.log_logout.assert_called_once_with("1", "admin")

    @pytest.mark.asyncio
    async def test_log_mfa_success(self, service, mock_repo):
        result = await service.log_mfa("1", "admin", True)
        assert result["_id"] == 3
        mock_repo.log_mfa_verification.assert_called_once_with("1", "admin", True)

    @pytest.mark.asyncio
    async def test_log_mfa_failed(self, service, mock_repo):
        await service.log_mfa("1", "admin", False)
        mock_repo.log_mfa_verification.assert_called_once_with("1", "admin", False)

    @pytest.mark.asyncio
    async def test_log_user_creation(self, service, mock_repo):
        await service.log_user_creation("1", "newuser")
        mock_repo.log_user_management.assert_called_once_with(
            "1", "create_user", "newuser", {"by": "1"}
        )

    @pytest.mark.asyncio
    async def test_log_role_change(self, service, mock_repo):
        await service.log_role_change("1", "target", "lecteur", "analyste")
        mock_repo.log_user_management.assert_called_once_with(
            "1", "update_role", "target", {"old_role": "lecteur", "new_role": "analyste"}
        )


class TestGetAuditService:
    def test_get_audit_service_returns_instance(self):
        with patch("app.services.audit_service.get_es") as mock_get_es:
            with patch("app.services.audit_service.AuditRepository") as mock_repo:
                svc = get_audit_service()
                assert isinstance(svc, AuditService)

# app/tests/test_repositories/test_audit_repo.py
# -------------------------------
# Tests unitaires du repository Audit (app/repositories/audit_repo.py)

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.repositories.audit_repo import AuditRepository


@pytest.fixture
def db_session():
    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def repo(db_session):
    return AuditRepository(db_session)


def make_mock_log():
    log = MagicMock()
    log.id = 1
    log.user_id = 1
    log.username = "admin"
    log.action = "login"
    log.resource_type = None
    log.resource_id = None
    log.details = {}
    log.ip_address = "10.0.0.1"
    log.user_agent = None
    log.result = "success"
    log.created_at = datetime.now(timezone.utc)
    return log


class TestAuditLogAction:
    @pytest.mark.asyncio
    async def test_log_action(self, repo, db_session):
        mock_log = make_mock_log()
        db_session.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'id', 1))

        with patch("app.repositories.audit_repo.AuditLog", return_value=mock_log):
            result = await repo.log_action({
                "user_id": 1, "username": "admin", "action": "login",
                "result": "success", "ip_address": "10.0.0.1",
            })
            assert result["action"] == "login"
            assert result["result"] == "success"
            assert result["_id"] == 1


class TestAuditLoginAttempt:
    @pytest.mark.asyncio
    async def test_login_success(self, repo, db_session):
        mock_log = make_mock_log()
        mock_log.action = "login"
        mock_log.result = "success"
        db_session.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'id', 1))

        with patch("app.repositories.audit_repo.AuditLog", return_value=mock_log):
            result = await repo.log_login_attempt("1", "admin", True, "10.0.0.1")
            assert result["action"] == "login"
            assert result["result"] == "success"

    @pytest.mark.asyncio
    async def test_login_failed(self, repo, db_session):
        mock_log = make_mock_log()
        mock_log.action = "login"
        mock_log.result = "failed"
        db_session.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'id', 1))

        with patch("app.repositories.audit_repo.AuditLog", return_value=mock_log):
            result = await repo.log_login_attempt("1", "admin", False, "10.0.0.1")
            assert result["result"] == "failed"

    @pytest.mark.asyncio
    async def test_login_system_user(self, repo, db_session):
        mock_log = make_mock_log()
        mock_log.user_id = None
        db_session.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'id', 1))

        with patch("app.repositories.audit_repo.AuditLog", return_value=mock_log):
            result = await repo.log_login_attempt("system", "system", True)
            assert result is not None


class TestAuditLogout:
    @pytest.mark.asyncio
    async def test_logout(self, repo, db_session):
        mock_log = make_mock_log()
        mock_log.action = "logout"
        db_session.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'id', 1))

        with patch("app.repositories.audit_repo.AuditLog", return_value=mock_log):
            result = await repo.log_logout("1", "admin")
            assert result["action"] == "logout"


class TestAuditMFA:
    @pytest.mark.asyncio
    async def test_mfa_success(self, repo, db_session):
        mock_log = make_mock_log()
        mock_log.action = "mfa_verify"
        mock_log.result = "success"
        db_session.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'id', 1))

        with patch("app.repositories.audit_repo.AuditLog", return_value=mock_log):
            result = await repo.log_mfa_verification("1", "admin", True)
            assert result["action"] == "mfa_verify"
            assert result["result"] == "success"


class TestAuditUserManagement:
    @pytest.mark.asyncio
    async def test_create_user(self, repo, db_session):
        mock_log = make_mock_log()
        mock_log.action = "create_user"
        db_session.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'id', 1))

        with patch("app.repositories.audit_repo.AuditLog", return_value=mock_log):
            result = await repo.log_user_management("1", "create_user", "newuser", {"role": "analyste"})
            assert result["action"] == "create_user"

    @pytest.mark.asyncio
    async def test_update_role(self, repo, db_session):
        mock_log = MagicMock()
        mock_log.id = 1
        mock_log.action = "update_role"
        mock_log.result = "success"
        mock_log.user_id = 1
        mock_log.username = "target"
        mock_log.created_at = datetime.now(timezone.utc)
        db_session.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'id', 1))

        with patch("app.repositories.audit_repo.AuditLog", return_value=mock_log):
            result = await repo.log_user_management(
                "1", "update_role", "target",
                {"old_role": "lecteur", "new_role": "analyste"}
            )
            assert result["action"] == "update_role"


class TestAuditGetLogs:
    @pytest.mark.asyncio
    async def test_get_logs_empty(self, repo, db_session):
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        db_session.execute.return_value = result_mock
        logs = await repo.get_audit_logs()
        assert logs == []

    @pytest.mark.asyncio
    async def test_get_logs_with_filter(self, repo, db_session):
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        db_session.execute.return_value = result_mock
        logs = await repo.get_audit_logs(filters={"action": "login"})
        assert logs == []


class TestAuditDeleteOlderThan:
    @pytest.mark.asyncio
    async def test_delete_older_than(self, repo, db_session):
        result_mock = MagicMock()
        result_mock.rowcount = 5
        db_session.execute.return_value = result_mock
        deleted = await repo.delete_older_than(90)
        assert deleted == 5

    @pytest.mark.asyncio
    async def test_delete_older_than_zero(self, repo, db_session):
        result_mock = MagicMock()
        result_mock.rowcount = 0
        db_session.execute.return_value = result_mock
        deleted = await repo.delete_older_than(90)
        assert deleted == 0

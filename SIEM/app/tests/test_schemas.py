# app/tests/test_schemas.py
# -------------------------------
# Tests des schémas Pydantic (validation)

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError
from app.schemas.user_schemas import UserCreate, UserLogin, UserResponse, UserUpdateRole, UserUpdatePerimeter
from app.schemas.log_schemas import LogCreate, LogResponse, LogListResponse, LogSearchRequest
from app.utils.tags import Role, Perimeter


class TestUserSchemas:

    def test_user_create_valid(self):
        user = UserCreate(
            username="testuser",
            email="test@mail.com",
            password="password123",
            role="analyste",
            perimeter=["equipe"],
        )
        assert user.username == "testuser"
        assert user.role == Role.ANALYSTE
        assert user.perimeter == [Perimeter.EQUIPE]

    def test_user_create_default_perimeter(self):
        user = UserCreate(
            username="testuser",
            email="test@mail.com",
            password="password123",
            role="lecteur",
        )
        assert user.perimeter == []

    def test_user_create_username_too_short(self):
        with pytest.raises(ValidationError):
            UserCreate(
                username="ab",
                email="test@mail.com",
                password="password123",
                role="lecteur",
            )

    def test_user_create_password_too_short(self):
        with pytest.raises(ValidationError):
            UserCreate(
                username="testuser",
                email="test@mail.com",
                password="123",
                role="lecteur",
            )

    def test_user_create_invalid_email(self):
        with pytest.raises(ValidationError):
            UserCreate(
                username="testuser",
                email="pas-un-email",
                password="password123",
                role="lecteur",
            )

    def test_user_create_invalid_role(self):
        with pytest.raises(ValidationError):
            UserCreate(
                username="testuser",
                email="test@mail.com",
                password="password123",
                role="superadmin",
            )

    def test_user_login_valid(self):
        login = UserLogin(username="admin", password="password123")
        assert login.username == "admin"
        assert login.password == "password123"
        assert login.mfa_code is None

    def test_user_login_with_mfa(self):
        login = UserLogin(username="admin", password="password123", mfa_code="123456")
        assert login.mfa_code == "123456"

    def test_user_response_valid(self):
        response = UserResponse(
            id=1,
            username="admin",
            email="admin@mail.com",
            role="administrateur",
            perimeter=["equipe"],
            mfa_enabled=False,
            created_at=datetime.now(timezone.utc),
        )
        assert response.id == 1
        assert response.role == Role.ADMINISTRATEUR

    def test_user_update_role_valid(self):
        update = UserUpdateRole(role="analyste")
        assert update.role == Role.ANALYSTE

    def test_user_update_perimeter_valid(self):
        update = UserUpdatePerimeter(perimeter=["equipe", "service"])
        assert Perimeter.EQUIPE in update.perimeter
        assert Perimeter.SERVICE in update.perimeter


class TestLogSchemas:

    def test_log_create_valid(self):
        log = LogCreate(
            timestamp=datetime.now(timezone.utc),
            source_ip="192.168.1.1",
            host="server-01",
            severity="error",
            raw_message="Failed password",
        )
        assert log.source_ip == "192.168.1.1"
        assert log.severity == "error"
        assert log.log_type is None

    def test_log_create_default_severity(self):
        log = LogCreate(
            timestamp=datetime.now(timezone.utc),
            source_ip="192.168.1.1",
            host="server-01",
            raw_message="Info message",
        )
        assert log.severity == "info"

    def test_log_create_invalid_severity(self):
        with pytest.raises(ValidationError):
            LogCreate(
                timestamp=datetime.now(timezone.utc),
                source_ip="192.168.1.1",
                host="server-01",
                severity="urgent",
                raw_message="test",
            )

    def test_log_response_valid(self):
        response = LogResponse(
            id="abc123",
            timestamp=datetime.now(timezone.utc),
            source_ip="10.0.0.1",
            host="server-01",
            severity="critical",
            raw_message="Attack detected",
            tags=["critical", "auth"],
        )
        assert response.id == "abc123"
        assert "critical" in response.tags

    def test_log_list_response_valid(self):
        log = LogResponse(
            id="1", timestamp=datetime.now(timezone.utc),
            source_ip="10.0.0.1", host="server-01",
            severity="info", raw_message="test",
        )
        list_resp = LogListResponse(items=[log], total=1, page=1, size=50, pages=1)
        assert list_resp.total == 1
        assert list_resp.page == 1

    def test_log_search_request_defaults(self):
        search = LogSearchRequest()
        assert search.query == "*"
        assert search.page == 1
        assert search.size == 50
        assert search.source_ips == []

    def test_log_search_request_with_filters(self):
        search = LogSearchRequest(
            query="Failed password",
            source_ips=["192.168.1.1"],
            severities=["critical"],
            page=2,
            size=10,
        )
        assert search.query == "Failed password"
        assert "192.168.1.1" in search.source_ips
        assert search.page == 2

# app/tests/test_api/test_auth_api.py
# -------------------------------
# Tests API pour l'authentification et les accès

import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestLoginEndpoint:
    def test_login_missing_fields(self):
        with TestClient(app) as client:
            resp = client.post("/api/v1/auth/login", json={})
            assert resp.status_code == 422

    def test_login_wrong_method(self):
        with TestClient(app) as client:
            resp = client.get("/api/v1/auth/login")
            assert resp.status_code == 405


class TestHealthEndpoint:
    def test_health(self):
        with TestClient(app) as client:
            resp = client.get("/health")
            assert resp.status_code == 200
            assert resp.json() == {"status": "ok"}

    def test_root(self):
        with TestClient(app) as client:
            resp = client.get("/")
            assert resp.status_code == 200
            assert "message" in resp.json()


class TestProtectedEndpoints:
    """Tests d'accès aux endpoints protégés (sans token → 401)."""

    @pytest.mark.parametrize("endpoint", [
        "/api/v1/ueba/profile/test",
        "/api/v1/ueba/scores",
        "/api/v1/users/",
        "/api/v1/rules/",
        "/api/v1/incidents/",
        "/api/v1/alerts/",
        "/api/v1/investigations/",
        "/api/v1/notifications/",
        "/api/v1/playbooks/",
    ])
    def test_endpoint_requires_auth(self, endpoint):
        with TestClient(app) as client:
            resp = client.get(endpoint)
            assert resp.status_code == 401

    def test_admin_purge_requires_auth(self):
        with TestClient(app) as client:
            resp = client.post("/api/v1/admin/purge/logs")
            assert resp.status_code == 401


class TestLogIngestEndpoint:
    def test_ingest_no_auth(self):
        """L'ingestion est publique."""
        with TestClient(app) as client:
            resp = client.post("/api/v1/logs/ingest", json={"raw_message": "test"})
            assert resp.status_code in (200, 503)

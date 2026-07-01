# app/tests/test_api/test_logs_api.py
# -------------------------------
# Tests API pour les logs (tests unitaires sans infrastructure)

import pytest
from fastapi.testclient import TestClient
from app.main import app

# Note : les tests qui nécessitent ES/PostgreSQL sont marqués
# integration et ne passent que si l'infrastructure est disponible


class TestListLogsEndpoint:
    def test_list_logs_requires_auth(self):
        with TestClient(app) as client:
            resp = client.get("/api/v1/logs/")
            assert resp.status_code == 401


class TestSearchLogsEndpoint:
    def test_search_requires_auth(self):
        with TestClient(app) as client:
            resp = client.post("/api/v1/logs/search", json={})
            assert resp.status_code == 401


class TestTimelineEndpoint:
    def test_timeline_requires_auth(self):
        with TestClient(app) as client:
            resp = client.get("/api/v1/logs/timeline")
            assert resp.status_code == 401


class TestIngestEndpoint:
    def test_ingest_no_auth_required(self):
        """L'ingestion est publique - pas de token requis.
        Skip car nécessite Redis/PostgreSQL pour le lifespan."""
        pytest.skip("Test d'intégration nécessitant Redis+PostgreSQL")

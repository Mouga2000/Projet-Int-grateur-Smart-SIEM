# app/tests/test_api/test_ueba_api.py
# -------------------------------
# Tests API pour UEBA

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies import get_current_user, get_db


class TestUEBAProfileEndpoint:
    def test_get_profile_missing_auth(self):
        with TestClient(app) as c:
            resp = c.get("/api/v1/ueba/profile/test-user")
            assert resp.status_code == 401

    def test_get_profile_invalid_token(self):
        with TestClient(app) as c:
            resp = c.get("/api/v1/ueba/profile/test-user",
                         headers={"Authorization": "Bearer invalid"})
            assert resp.status_code == 401

    def test_get_nonexistent_profile_with_auth(self):
        """Test avec mock DB - nécessite Redis/PostgreSQL pour le lifespan."""
        pytest.skip("Test d'intégration nécessitant Redis+PostgreSQL")


class TestUEBAScoresEndpoint:
    def test_scores_missing_auth(self):
        with TestClient(app) as c:
            resp = c.get("/api/v1/ueba/scores")
            assert resp.status_code == 401

    def test_lecteur_cannot_access_scores(self):
        """Un lecteur n'a pas accès aux scores UEBA."""
        pytest.skip("Test d'intégration nécessitant Redis+PostgreSQL")

    def test_scores_with_mock_db(self):
        """Test avec mock DB."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=MagicMock(
            scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
        ))
        async def override_get_current_user():
            return {"id": 1, "username": "admin", "role": "administrateur",
                    "perimeter": [], "is_active": True}
        async def override_get_db():
            yield mock_db

        app.dependency_overrides[get_current_user] = override_get_current_user
        app.dependency_overrides[get_db] = override_get_db

        with TestClient(app) as c:
            resp = c.get("/api/v1/ueba/scores?min_score=0&limit=10")
            assert resp.status_code == 200
            data = resp.json()
            assert "items" in data
            assert "total" in data

    def test_scores_invalid_params(self):
        """Validation des paramètres."""
        mock_db = MagicMock()
        async def override_get_current_user():
            return {"id": 1, "username": "admin", "role": "administrateur",
                    "perimeter": [], "is_active": True}
        async def override_get_db():
            yield mock_db

        app.dependency_overrides[get_current_user] = override_get_current_user
        app.dependency_overrides[get_db] = override_get_db

        with TestClient(app) as c:
            resp = c.get("/api/v1/ueba/scores?limit=1000")
            assert resp.status_code == 422

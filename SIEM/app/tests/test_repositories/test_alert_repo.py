# app/tests/test_repositories/test_alert_repo.py
# -------------------------------
# Tests unitaires du repository Alert (app/repositories/alert_repo.py)

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.repositories.alert_repo import AlertRepository


@pytest.fixture
def db_session():
    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def alert_repo(db_session):
    return AlertRepository(db_session)


class TestAlertCreate:
    """Tests de création d'alerte."""

    @pytest.mark.asyncio
    async def test_create_with_all_fields(self, alert_repo, db_session):
        from app.models.sql_models import Alert
        mock_alert = MagicMock()
        mock_alert.id = 1
        db_session.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'id', 1))

        with patch("app.repositories.alert_repo.Alert", return_value=mock_alert) as mock_alert_class:
            data = {
                "rule_id": 42, "rule_name": "Test Rule", "description": "Desc",
                "severity": "high", "source_ip": "10.0.0.5", "host": "srv-01",
                "mitre": {"technique": "T1078"}, "score": 80,
            }
            alert_id = await alert_repo.create(data)
            assert alert_id == mock_alert.id
            mock_alert_class.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_minimal(self, alert_repo, db_session):
        from app.models.sql_models import Alert
        mock_alert = MagicMock()
        mock_alert.id = 2
        db_session.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'id', 2))

        with patch("app.repositories.alert_repo.Alert", return_value=mock_alert):
            alert_id = await alert_repo.create({"rule_name": "Minimal Alert"})
            assert alert_id == 2


class TestAlertGetById:
    """Tests de récupération d'une alerte par ID."""

    @pytest.mark.asyncio
    async def test_get_existing_alert(self, alert_repo, db_session):
        from app.models.sql_models import Alert
        mock_alert = MagicMock()
        mock_alert.id = 1
        mock_alert.regle_id = 42
        mock_alert.titre = "Test Alert"
        mock_alert.description = "Desc"
        mock_alert.niveau = "high"
        mock_alert.source_ip = "10.0.0.5"
        mock_alert.host = "srv-01"
        mock_alert.statut = "ouverte"
        mock_alert.score_confiance = 80
        mock_alert.mitre = {}
        mock_alert.cree_le = datetime.now(timezone.utc)
        mock_alert.updated_at = datetime.now(timezone.utc)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_alert
        db_session.execute.return_value = result_mock

        alert = await alert_repo.get_by_id(1)
        assert alert is not None
        assert alert["id"] == 1
        assert alert["title"] == "Test Alert"

    @pytest.mark.asyncio
    async def test_get_nonexistent_alert(self, alert_repo, db_session):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        db_session.execute.return_value = result_mock
        alert = await alert_repo.get_by_id(999)
        assert alert is None


class TestAlertSearch:
    """Tests de recherche d'alertes."""

    @pytest.mark.asyncio
    async def test_search_without_filters(self, alert_repo, db_session):
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        db_session.execute.return_value = result_mock
        result = await alert_repo.search(filters={}, page=1, size=50)
        assert "items" in result
        assert "total" in result

    @pytest.mark.asyncio
    async def test_search_with_severity_filter(self, alert_repo, db_session):
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        db_session.execute.return_value = result_mock
        await alert_repo.search(filters={"niveau": "critical"}, page=1, size=50)
        # Vérifie que la requête a été exécutée
        assert db_session.execute.called


class TestAlertUpdate:
    """Tests de mise à jour d'alerte."""

    @pytest.mark.asyncio
    async def test_update_status(self, alert_repo, db_session):
        from app.models.sql_models import Alert
        mock_alert = MagicMock()
        mock_alert.statut = "ouverte"
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_alert
        db_session.execute.return_value = result_mock

        result = await alert_repo.update(1, {"statut": "resolue"})
        assert result is True
        assert mock_alert.statut == "resolue"

    @pytest.mark.asyncio
    async def test_update_nonexistent(self, alert_repo, db_session):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        db_session.execute.return_value = result_mock
        result = await alert_repo.update(999, {"statut": "resolue"})
        assert result is False

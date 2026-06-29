# app/tests/test_repositories/test_incident_repo.py
# -------------------------------
# Tests unitaires du repository Incident (app/repositories/incident_repo.py)

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.repositories.incident_repo import IncidentRepository


@pytest.fixture
def db_session():
    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def incident_repo(db_session):
    return IncidentRepository(db_session)


class TestIncidentCreate:
    @pytest.mark.asyncio
    async def test_create_with_timeline(self, incident_repo, db_session):
        from app.models.sql_models import Incident
        mock_inc = MagicMock()
        mock_inc.id = 1
        mock_inc.statut = "ouverte"
        mock_inc.assigne_a = None
        mock_inc.alert_ids = []
        mock_inc.rule_ids = []
        mock_inc.mitre_attack_ids = []
        mock_inc.notes_resolution = None
        mock_inc.timeline = []
        mock_inc.closed_at = None
        mock_inc.cree_le = MagicMock()

        # Simuler le constructeur en renvoyant un mock avec les bons attributs
        def make_incident(**kwargs):
            for k, v in kwargs.items():
                setattr(mock_inc, k, v)
            return mock_inc

        with patch("app.repositories.incident_repo.Incident", side_effect=make_incident):
            mock_inc.id = 1
            mock_inc.cree_le = MagicMock()
            db_session.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'id', 1))
            result = await incident_repo.create({"created_by": 1, "alert_ids": [42]})
            assert result["id"] == 1
            assert len(result["timeline"]) == 1
            assert result["timeline"][0]["action"] == "created"


class TestIncidentGetById:
    @pytest.mark.asyncio
    async def test_get_existing(self, incident_repo, db_session):
        from app.models.sql_models import Incident
        mock_inc = MagicMock()
        mock_inc.id = 1
        mock_inc.statut = "ouverte"
        mock_inc.assigne_a = None
        mock_inc.alert_ids = []
        mock_inc.rule_ids = []
        mock_inc.mitre_attack_ids = []
        mock_inc.notes_resolution = None
        mock_inc.timeline = []
        mock_inc.closed_at = None
        mock_inc.cree_le = MagicMock()

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_inc
        db_session.execute.return_value = result_mock

        inc = await incident_repo.get_by_id(1)
        assert inc is not None
        assert inc["statut"] == "ouverte"

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, incident_repo, db_session):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        db_session.execute.return_value = result_mock
        inc = await incident_repo.get_by_id(999)
        assert inc is None


class TestIncidentUpdateStatus:
    @pytest.mark.asyncio
    async def test_update_status_adds_timeline_entry(self, incident_repo, db_session):
        from app.models.sql_models import Incident
        mock_inc = MagicMock()
        mock_inc.statut = "ouverte"
        mock_inc.timeline = []
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_inc
        db_session.execute.return_value = result_mock

        result = await incident_repo.update_status(1, "en_cours", user_id=1, notes=None)
        assert result is True
        assert mock_inc.statut == "en_cours"
        assert len(mock_inc.timeline) == 1
        assert mock_inc.timeline[0]["action"] == "status_change"

    @pytest.mark.asyncio
    async def test_update_status_with_notes(self, incident_repo, db_session):
        from app.models.sql_models import Incident
        mock_inc = MagicMock()
        mock_inc.statut = "ouverte"
        mock_inc.timeline = []
        mock_inc.notes_resolution = None
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_inc
        db_session.execute.return_value = result_mock

        await incident_repo.update_status(1, "resolue", user_id=1, notes="Corrigé")
        assert mock_inc.notes_resolution == "Corrigé"

    @pytest.mark.asyncio
    async def test_update_status_nonexistent(self, incident_repo, db_session):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        db_session.execute.return_value = result_mock
        result = await incident_repo.update_status(999, "resolue")
        assert result is False


class TestIncidentAddAlert:
    @pytest.mark.asyncio
    async def test_add_alert_updates_timeline(self, incident_repo, db_session):
        from app.models.sql_models import Incident
        mock_inc = MagicMock()
        mock_inc.alert_ids = []
        mock_inc.timeline = []
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_inc
        db_session.execute.return_value = result_mock

        result = await incident_repo.add_alert(1, 42, user_id=1)
        assert result is True
        assert 42 in mock_inc.alert_ids
        assert mock_inc.timeline[0]["action"] == "alert_added"

    @pytest.mark.asyncio
    async def test_add_duplicate_alert(self, incident_repo, db_session):
        from app.models.sql_models import Incident
        mock_inc = MagicMock()
        mock_inc.alert_ids = [42]
        mock_inc.timeline = []
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_inc
        db_session.execute.return_value = result_mock

        await incident_repo.add_alert(1, 42, user_id=1)
        # L'alerte n'est pas dupliquée
        assert mock_inc.alert_ids == [42]


class TestIncidentAssign:
    @pytest.mark.asyncio
    async def test_assign_user(self, incident_repo, db_session):
        from app.models.sql_models import Incident
        mock_inc = MagicMock()
        mock_inc.assigne_a = None
        mock_inc.timeline = []
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_inc
        db_session.execute.return_value = result_mock

        result = await incident_repo.assign(1, 5, assigned_by=1)
        assert result is True
        assert mock_inc.assigne_a == 5
        assert mock_inc.timeline[0]["action"] == "assigned"


class TestIncidentList:
    @pytest.mark.asyncio
    async def test_list_all(self, incident_repo, db_session):
        from app.models.sql_models import Incident
        mock_inc = MagicMock()
        mock_inc.id = 1
        mock_inc.statut = "ouverte"
        mock_inc.assigne_a = None
        mock_inc.alert_ids = []
        mock_inc.rule_ids = []
        mock_inc.mitre_attack_ids = []
        mock_inc.notes_resolution = None
        mock_inc.timeline = []
        mock_inc.closed_at = None
        mock_inc.cree_le = MagicMock()

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [mock_inc]
        db_session.execute.return_value = result_mock

        # Créer un second result mock pour le count (appelé 2×)
        result_mock2 = MagicMock()
        result_mock2.scalars.return_value.all.return_value = [mock_inc]
        db_session.execute.side_effect = [result_mock, result_mock2]

        result = await incident_repo.list_incidents()
        assert result["total"] == 1
        assert len(result["items"]) == 1

    @pytest.mark.asyncio
    async def test_list_with_status_filter(self, incident_repo, db_session):
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        db_session.execute.return_value = result_mock

        result = await incident_repo.list_incidents(statut="ouverte")
        assert result["total"] == 0

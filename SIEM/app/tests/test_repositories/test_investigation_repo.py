# app/tests/test_repositories/test_investigation_repo.py
# -------------------------------
# Tests unitaires du repository Investigation (app/repositories/investigation_repo.py)

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.repositories.investigation_repo import InvestigationRepository


@pytest.fixture
def db_session():
    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def inv_repo(db_session):
    return InvestigationRepository(db_session)


class TestInvestigationCreate:
    @pytest.mark.asyncio
    async def test_create_minimal(self, inv_repo, db_session):
        from app.models.sql_models import Investigation
        mock_inv = MagicMock()
        mock_inv.id = 1
        mock_inv.title = "Test Investigation"
        mock_inv.severity = "medium"
        mock_inv.tags = []
        mock_inv.log_ids = []
        mock_inv.mitre_tactic = None
        mock_inv.mitre_technique = None
        mock_inv.created_by = 1
        mock_inv.status = "ouverte"
        mock_inv.assigned_to = None
        mock_inv.closed_at = None
        mock_inv.resolution_notes = None
        mock_inv.description = None
        mock_inv.created_at = MagicMock()
        mock_inv.updated_at = MagicMock()
        db_session.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'id', 1))

        with patch("app.repositories.investigation_repo.Investigation", return_value=mock_inv):
            result = await inv_repo.create({"title": "Test Investigation", "created_by": 1})
            assert result["id"] == 1
            assert result["title"] == "Test Investigation"


class TestInvestigationGetById:
    @pytest.mark.asyncio
    async def test_get_existing(self, inv_repo, db_session):
        from app.models.sql_models import Investigation
        mock_inv = MagicMock()
        mock_inv.id = 1
        mock_inv.title = "Test"
        mock_inv.status = "ouverte"

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_inv
        db_session.execute.return_value = result_mock

        inv = await inv_repo.get_by_id(1)
        assert inv is not None

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, inv_repo, db_session):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        db_session.execute.return_value = result_mock
        inv = await inv_repo.get_by_id(999)
        assert inv is None


class TestInvestigationAddLog:
    @pytest.mark.asyncio
    async def test_add_log_creates_link(self, inv_repo, db_session):
        from app.models.sql_models import Investigation, InvestigationLog
        mock_inv = MagicMock()
        mock_inv.log_ids = []
        mock_link = MagicMock(spec=InvestigationLog)
        mock_link.id = 1
        mock_link.investigation_id = 1
        mock_link.log_id = "abc123"
        mock_link.analyst_note = "Suspicious"
        mock_link.analyst_verdict = "suspect"
        mock_link.added_by = 1
        mock_link.created_at = MagicMock()

        result_inv = MagicMock()
        result_inv.scalar_one_or_none.return_value = mock_inv
        db_session.execute.return_value = result_inv
        db_session.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'id', 1))

        with patch("app.repositories.investigation_repo.InvestigationLog", return_value=mock_link):
            result = await inv_repo.add_log(1, "abc123", note="Suspicious", verdict="suspect", user_id=1)
            assert result["log_id"] == "abc123"
            assert result["verdict"] == "suspect"

    @pytest.mark.asyncio
    async def test_add_log_updates_investigation_log_ids(self, inv_repo, db_session):
        from app.models.sql_models import Investigation, InvestigationLog
        mock_inv = MagicMock()
        mock_inv.log_ids = []
        mock_link = MagicMock(spec=InvestigationLog)
        mock_link.id = 1
        mock_link.investigation_id = 1
        mock_link.log_id = "abc123"
        mock_link.analyst_note = None
        mock_link.analyst_verdict = "suspect"
        mock_link.added_by = 1
        mock_link.created_at = MagicMock()

        result_inv = MagicMock()
        result_inv.scalar_one_or_none.return_value = mock_inv
        db_session.execute.return_value = result_inv
        db_session.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'id', 1))

        with patch("app.repositories.investigation_repo.InvestigationLog", return_value=mock_link):
            await inv_repo.add_log(1, "abc123", user_id=1)
            assert "abc123" in mock_inv.log_ids


class TestInvestigationList:
    @pytest.mark.asyncio
    async def test_list_all(self, inv_repo, db_session):
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        db_session.execute.return_value = result_mock

        items = await inv_repo.list_investigations()
        assert items == []

    @pytest.mark.asyncio
    async def test_list_with_status(self, inv_repo, db_session):
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        db_session.execute.return_value = result_mock

        items = await inv_repo.list_investigations(status="ouverte")
        assert items == []


class TestInvestigationUpdate:
    @pytest.mark.asyncio
    async def test_update(self, inv_repo, db_session):
        from app.models.sql_models import Investigation
        mock_inv = MagicMock()
        mock_inv.title = "Old Title"
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_inv
        db_session.execute.return_value = result_mock

        result = await inv_repo.update(1, {"title": "New Title"})
        assert result is True
        assert mock_inv.title == "New Title"

    @pytest.mark.asyncio
    async def test_update_status(self, inv_repo, db_session):
        from app.models.sql_models import Investigation
        mock_inv = MagicMock()
        mock_inv.status = "ouverte"
        mock_inv.resolution_notes = None
        mock_inv.closed_at = None
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_inv
        db_session.execute.return_value = result_mock

        result = await inv_repo.update_status(1, "resolue", notes="All good")
        assert result is True
        assert mock_inv.status == "resolue"

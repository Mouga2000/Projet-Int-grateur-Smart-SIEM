# app/tests/test_repositories/test_playbook_repo.py
# -------------------------------
# Tests unitaires du repository Playbook (app/repositories/playbook_repo.py)

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.repositories.playbook_repo import PlaybookRepository


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
    return PlaybookRepository(db_session)


class TestPlaybookCreate:
    @pytest.mark.asyncio
    async def test_create_minimal(self, repo, db_session):
        mock_pb = MagicMock()
        mock_pb.id = 1
        mock_pb.name = "Test"
        mock_pb.trigger = "manual"
        mock_pb.enabled = True
        mock_pb.steps = []
        mock_pb.variables = {}
        mock_pb.timeout_seconds = 300
        mock_pb.max_retries = 3
        mock_pb.execution_count = 0
        mock_pb.last_executed_at = None
        mock_pb.created_by = None
        mock_pb.created_at = datetime.now(timezone.utc)
        mock_pb.updated_at = datetime.now(timezone.utc)
        mock_pb.description = None
        mock_pb.id = 1  # already set, refresh won't change it
        db_session.refresh = AsyncMock()

        def make_pb(**kw):
            for k, v in kw.items():
                setattr(mock_pb, k, v)
            return mock_pb

        with patch("app.repositories.playbook_repo.Playbook", side_effect=make_pb):
            result = await repo.create({"name": "Test Playbook"})
            assert result["name"] == "Test Playbook"
            assert result["trigger"] == "manual"

    @pytest.mark.asyncio
    async def test_create_full(self, repo, db_session):
        mock_pb = MagicMock()
        mock_pb.id = 2
        mock_pb.name = "Full"
        mock_pb.trigger = "alert_created"
        mock_pb.enabled = True
        mock_pb.steps = [{"action": "block_ip"}]
        mock_pb.variables = {}
        mock_pb.timeout_seconds = 600
        mock_pb.max_retries = 5
        mock_pb.execution_count = 0
        mock_pb.last_executed_at = None
        mock_pb.created_by = "admin"
        mock_pb.created_at = datetime.now(timezone.utc)
        mock_pb.updated_at = datetime.now(timezone.utc)
        mock_pb.description = None
        mock_pb.id = 2
        db_session.refresh = AsyncMock()

        def make_pb(**kw):
            for k, v in kw.items():
                setattr(mock_pb, k, v)
            return mock_pb

        with patch("app.repositories.playbook_repo.Playbook", side_effect=make_pb):
            result = await repo.create({
                "name": "Full Playbook", "trigger": "alert_created",
                "steps": [{"action": "block_ip"}], "created_by": "admin",
            })
            assert result["name"] == "Full Playbook"


class TestPlaybookGetById:
    @pytest.mark.asyncio
    async def test_get_existing(self, repo, db_session):
        mock_pb = MagicMock()
        mock_pb.id = 1
        mock_pb.name = "Test"
        mock_pb.created_at = datetime.now(timezone.utc)
        mock_pb.updated_at = datetime.now(timezone.utc)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_pb
        db_session.execute.return_value = result_mock

        pb = await repo.get_by_id(1)
        assert pb is not None
        assert pb["name"] == "Test"

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, repo, db_session):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        db_session.execute.return_value = result_mock
        pb = await repo.get_by_id(999)
        assert pb is None


class TestPlaybookGetEnabled:
    @pytest.mark.asyncio
    async def test_get_enabled(self, repo, db_session):
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        db_session.execute.return_value = result_mock
        result = await repo.get_enabled_playbooks()
        assert result == []


class TestPlaybookGetByTrigger:
    @pytest.mark.asyncio
    async def test_get_by_trigger(self, repo, db_session):
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        db_session.execute.return_value = result_mock
        result = await repo.get_by_trigger("alert_created")
        assert result == []


class TestPlaybookUpdate:
    @pytest.mark.asyncio
    async def test_update(self, repo, db_session):
        mock_pb = MagicMock()
        mock_pb.enabled = True
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_pb
        db_session.execute.return_value = result_mock

        result = await repo.update(1, {"enabled": False})
        assert result is True
        assert mock_pb.enabled is False

    @pytest.mark.asyncio
    async def test_update_nonexistent(self, repo, db_session):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        db_session.execute.return_value = result_mock
        result = await repo.update(999, {"enabled": False})
        assert result is False


class TestPlaybookIncrementExecution:
    @pytest.mark.asyncio
    async def test_increment(self, repo, db_session):
        mock_pb = MagicMock()
        mock_pb.execution_count = 5
        mock_pb.last_executed_at = None
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_pb
        db_session.execute.return_value = result_mock

        result = await repo.increment_execution(1)
        assert result is True
        assert mock_pb.execution_count == 6

    @pytest.mark.asyncio
    async def test_increment_first_time(self, repo, db_session):
        mock_pb = MagicMock()
        mock_pb.execution_count = None
        mock_pb.last_executed_at = None
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_pb
        db_session.execute.return_value = result_mock

        result = await repo.increment_execution(1)
        assert result is True
        assert mock_pb.execution_count == 1

    @pytest.mark.asyncio
    async def test_increment_nonexistent(self, repo, db_session):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        db_session.execute.return_value = result_mock
        result = await repo.increment_execution(999)
        assert result is False


class TestPlaybookDelete:
    @pytest.mark.asyncio
    async def test_soft_delete(self, repo, db_session):
        mock_pb = MagicMock()
        mock_pb.deleted_at = None
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_pb
        db_session.execute.return_value = result_mock

        result = await repo.delete(1)
        assert result is True
        assert mock_pb.deleted_at is not None

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, repo, db_session):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        db_session.execute.return_value = result_mock
        result = await repo.delete(999)
        assert result is False

# app/tests/test_repositories/test_archive_repo.py
# -------------------------------
# Tests unitaires du repository Archive (app/repositories/archive_repo.py)

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.repositories.archive_repo import ArchiveRepository


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
    return ArchiveRepository(db_session)


SAMPLE_ARCHIVE = {
    "date_from": datetime(2026, 1, 1, tzinfo=timezone.utc),
    "date_to": datetime(2026, 1, 31, tzinfo=timezone.utc),
    "log_count": 10000,
    "file_path": "/archives/archive_20260101.json.gz",
    "file_size_bytes": 1048576,
    "sha256_hash": "abc123",
    "merkle_root": "def456",
    "chain_hash": "ghi789",
    "previous_archive_id": None,
    "previous_hash": None,
    "timestamp_signature": "sig123",
    "created_by": 1,
}


class TestArchiveCreate:
    @pytest.mark.asyncio
    async def test_create(self, repo, db_session):
        mock_a = MagicMock()
        mock_a.id = 1
        mock_a.date_from = SAMPLE_ARCHIVE["date_from"]
        mock_a.date_to = SAMPLE_ARCHIVE["date_to"]
        mock_a.log_count = 10000
        mock_a.file_path = "/archives/test.json.gz"
        mock_a.file_size_bytes = 1048576
        mock_a.sha256_hash = "abc"
        mock_a.merkle_root = "def"
        mock_a.previous_archive_id = None
        mock_a.previous_hash = None
        mock_a.chain_hash = "ghi"
        mock_a.timestamp_signature = None
        mock_a.certified_by = "self"
        mock_a.certified_at = datetime.now(timezone.utc)
        mock_a.created_by = 1
        mock_a.status = "active"
        mock_a.verified_at = None
        mock_a.verified_by = None
        mock_a.created_at = datetime.now(timezone.utc)
        db_session.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'id', 1))

        with patch("app.repositories.archive_repo.Archive", return_value=mock_a):
            result = await repo.create(SAMPLE_ARCHIVE)
            assert result["log_count"] == 10000
            assert result["sha256_hash"] == "abc"

    @pytest.mark.asyncio
    async def test_create_chained(self, repo, db_session):
        mock_a = MagicMock()
        mock_a.id = 2
        mock_a.previous_archive_id = 1
        mock_a.previous_hash = "prev_hash"
        mock_a.chain_hash = "new_chain"
        mock_a.status = "active"
        mock_a.log_count = 5000
        mock_a.file_path = "/archives/test2.json.gz"
        mock_a.file_size_bytes = 512000
        mock_a.sha256_hash = "abc2"
        mock_a.merkle_root = "def2"
        mock_a.timestamp_signature = None
        mock_a.certified_by = "self"
        mock_a.certified_at = datetime.now(timezone.utc)
        mock_a.created_by = 1
        mock_a.verified_at = None
        mock_a.verified_by = None
        mock_a.created_at = datetime.now(timezone.utc)
        mock_a.date_from = SAMPLE_ARCHIVE["date_from"]
        mock_a.date_to = SAMPLE_ARCHIVE["date_to"]
        db_session.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'id', 2))

        data = {**SAMPLE_ARCHIVE, "previous_archive_id": 1, "previous_hash": "prev_hash"}
        with patch("app.repositories.archive_repo.Archive", return_value=mock_a):
            result = await repo.create(data)
            assert result["previous_archive_id"] == 1


class TestArchiveGetById:
    @pytest.mark.asyncio
    async def test_get_existing(self, repo, db_session):
        mock_a = MagicMock()
        mock_a.id = 1
        mock_a.log_count = 10000
        mock_a.date_from = SAMPLE_ARCHIVE["date_from"]
        mock_a.date_to = SAMPLE_ARCHIVE["date_to"]
        mock_a.file_path = "path"
        mock_a.file_size_bytes = 100
        mock_a.sha256_hash = "h"
        mock_a.merkle_root = "m"
        mock_a.chain_hash = "c"
        mock_a.certified_by = "self"
        mock_a.certified_at = datetime.now(timezone.utc)
        mock_a.created_at = datetime.now(timezone.utc)
        mock_a.previous_archive_id = None
        mock_a.previous_hash = None
        mock_a.timestamp_signature = None
        mock_a.created_by = None
        mock_a.status = "active"
        mock_a.verified_at = None
        mock_a.verified_by = None

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_a
        db_session.execute.return_value = result_mock

        arch = await repo.get_by_id(1)
        assert arch is not None
        assert arch["log_count"] == 10000

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, repo, db_session):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        db_session.execute.return_value = result_mock
        arch = await repo.get_by_id(999)
        assert arch is None


class TestArchiveGetLast:
    @pytest.mark.asyncio
    async def test_get_last(self, repo, db_session):
        mock_a = MagicMock()
        mock_a.id = 5
        mock_a.log_count = 100
        mock_a.date_from = SAMPLE_ARCHIVE["date_from"]
        mock_a.date_to = SAMPLE_ARCHIVE["date_to"]
        mock_a.file_path = "path"
        mock_a.file_size_bytes = 100
        mock_a.sha256_hash = "h"
        mock_a.merkle_root = "m"
        mock_a.chain_hash = "c"
        mock_a.certified_by = "self"
        mock_a.certified_at = datetime.now(timezone.utc)
        mock_a.created_at = datetime.now(timezone.utc)
        mock_a.previous_archive_id = None
        mock_a.previous_hash = None
        mock_a.timestamp_signature = None
        mock_a.created_by = None
        mock_a.status = "active"
        mock_a.verified_at = None
        mock_a.verified_by = None

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_a
        db_session.execute.return_value = result_mock

        last = await repo.get_last_archive()
        assert last is not None
        assert last["id"] == 5

    @pytest.mark.asyncio
    async def test_get_last_empty(self, repo, db_session):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        db_session.execute.return_value = result_mock
        last = await repo.get_last_archive()
        assert last is None


class TestArchiveList:
    @pytest.mark.asyncio
    async def test_list(self, repo, db_session):
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        db_session.execute.return_value = result_mock
        archives = await repo.list_archives()
        assert archives == []


class TestArchiveUpdateVerification:
    @pytest.mark.asyncio
    async def test_verify(self, repo, db_session):
        mock_a = MagicMock()
        mock_a.verified_at = None
        mock_a.verified_by = None
        mock_a.status = "active"
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_a
        db_session.execute.return_value = result_mock

        result = await repo.update_verification(1, user_id=1, status="verified")
        assert result is True
        assert mock_a.status == "verified"
        assert mock_a.verified_by == 1

    @pytest.mark.asyncio
    async def test_verify_nonexistent(self, repo, db_session):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        db_session.execute.return_value = result_mock
        result = await repo.update_verification(999, user_id=1)
        assert result is False


class TestArchiveCount:
    @pytest.mark.asyncio
    async def test_count(self, repo, db_session):
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [MagicMock(), MagicMock(), MagicMock()]
        db_session.execute.return_value = result_mock
        count = await repo.count()
        assert count == 3

    @pytest.mark.asyncio
    async def test_count_zero(self, repo, db_session):
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        db_session.execute.return_value = result_mock
        count = await repo.count()
        assert count == 0

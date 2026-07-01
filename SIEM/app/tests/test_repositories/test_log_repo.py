# app/tests/test_repositories/test_log_repo.py
# -------------------------------
# Tests unitaires du repository LogRepository
# (Elasticsearch mocké — pas de connexion réelle requise)

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta
from elasticsearch.exceptions import NotFoundError

from app.repositories.log_repo import LogRepository


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_es():
    """Instance AsyncElasticsearch entièrement mockée."""
    es = AsyncMock()
    return es


@pytest.fixture
def log_repo(mock_es):
    """LogRepository instancié avec l'ES mocké."""
    repo = LogRepository(mock_es)
    repo.index_prefix = "siem-logs"  # Surcharge pour les tests
    return repo


@pytest.fixture
def sample_log():
    return {
        "timestamp": "2026-06-27T10:00:00Z",
        "source_ip": "192.168.1.10",
        "host": "server-01",
        "severity": "critical",
        "log_type": "auth",
        "raw_message": "Failed password for admin",
        "tags": ["critical", "auth"],
    }


# =============================================================================
# Tests de _get_index_name()
# =============================================================================

class TestGetIndexName:

    def test_index_name_uses_today(self, log_repo):
        today = datetime.now().strftime("%Y-%m-%d")
        index = log_repo._get_index_name()
        assert index == f"siem-logs-{today}"

    def test_index_name_with_specific_date(self, log_repo):
        date = datetime(2026, 1, 15)
        index = log_repo._get_index_name(date)
        assert index == "siem-logs-2026-01-15"

    def test_index_name_format(self, log_repo):
        index = log_repo._get_index_name()
        parts = index.split("-")
        assert len(parts) == 5  # siem, logs, YYYY, MM, DD
        assert parts[0] == "siem"
        assert parts[1] == "logs"


# =============================================================================
# Tests de ingest()
# =============================================================================

class TestIngest:

    @pytest.mark.asyncio
    async def test_ingest_returns_log_with_id(self, log_repo, mock_es, sample_log):
        mock_es.index.return_value = {
            "_id": "abc123",
            "result": "created",
        }
        result = await log_repo.ingest(sample_log.copy())
        assert result["id"] == "abc123"
        assert result["source_ip"] == "192.168.1.10"

    @pytest.mark.asyncio
    async def test_ingest_calls_es_index(self, log_repo, mock_es, sample_log):
        mock_es.index.return_value = {"_id": "xyz789"}
        await log_repo.ingest(sample_log.copy())
        mock_es.index.assert_called_once()
        call_kwargs = mock_es.index.call_args
        assert call_kwargs[1].get("refresh") is True or call_kwargs[0]

    @pytest.mark.asyncio
    async def test_ingest_uses_today_index(self, log_repo, mock_es, sample_log):
        mock_es.index.return_value = {"_id": "abc"}
        await log_repo.ingest(sample_log.copy())
        index_used = mock_es.index.call_args[1].get("index") or mock_es.index.call_args[0][0]
        today = datetime.now().strftime("%Y-%m-%d")
        assert today in str(index_used)


# =============================================================================
# Tests de bulk_ingest()
# =============================================================================

class TestBulkIngest:

    @pytest.mark.asyncio
    async def test_bulk_ingest_empty_list_returns_zero(self, log_repo, mock_es):
        result = await log_repo.bulk_ingest([])
        assert result["indexed"] == 0
        assert result["errors"] == []
        mock_es.bulk.assert_not_called()

    @pytest.mark.asyncio
    async def test_bulk_ingest_calls_es_bulk(self, log_repo, mock_es):
        mock_es.bulk.return_value = {"items": [{"index": {"_id": "1"}}], "errors": False}
        logs = [{"raw_message": "log1"}, {"raw_message": "log2"}]
        result = await log_repo.bulk_ingest(logs)
        mock_es.bulk.assert_called_once()

    @pytest.mark.asyncio
    async def test_bulk_ingest_returns_indexed_and_errors(self, log_repo, mock_es):
        mock_es.bulk.return_value = {
            "items": [{"index": {"_id": "1"}}, {"index": {"_id": "2"}}],
            "errors": False,
        }
        logs = [{"raw_message": "log1"}, {"raw_message": "log2"}]
        result = await log_repo.bulk_ingest(logs)
        assert result["errors"] is False


# =============================================================================
# Tests de get_by_id()
# =============================================================================

class TestGetById:

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, log_repo, mock_es):
        mock_es.get.return_value = {
            "_id": "abc123",
            "_source": {
                "host": "server-01",
                "severity": "critical",
                "raw_message": "Attack detected",
            },
        }
        result = await log_repo.get_by_id("abc123")
        assert result is not None
        assert result["id"] == "abc123"
        assert result["host"] == "server-01"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found_returns_none(self, log_repo, mock_es):
        mock_es.get.side_effect = NotFoundError(
            message="Not found", meta=MagicMock(), body={}
        )
        result = await log_repo.get_by_id("nonexistent-id")
        assert result is None


# =============================================================================
# Tests de search()
# =============================================================================

class TestSearch:

    @pytest.mark.asyncio
    async def test_search_default_query(self, log_repo, mock_es):
        mock_es.search.return_value = {
            "hits": {
                "total": {"value": 0},
                "hits": [],
            }
        }
        result = await log_repo.search()
        assert result["total"] == 0
        assert result["items"] == []

    @pytest.mark.asyncio
    async def test_search_returns_items(self, log_repo, mock_es):
        mock_es.search.return_value = {
            "hits": {
                "total": {"value": 2},
                "hits": [
                    {"_id": "1", "_source": {"host": "server-01", "severity": "info"}},
                    {"_id": "2", "_source": {"host": "server-02", "severity": "critical"}},
                ],
            }
        }
        result = await log_repo.search()
        assert result["total"] == 2
        assert len(result["items"]) == 2
        assert result["items"][0]["id"] == "1"
        assert result["items"][1]["host"] == "server-02"

    @pytest.mark.asyncio
    async def test_search_pagination(self, log_repo, mock_es):
        mock_es.search.return_value = {
            "hits": {"total": {"value": 100}, "hits": []}
        }
        result = await log_repo.search(page=2, size=10)
        assert result["page"] == 2
        assert result["size"] == 10

    @pytest.mark.asyncio
    async def test_search_pages_calculation(self, log_repo, mock_es):
        mock_es.search.return_value = {
            "hits": {"total": {"value": 95}, "hits": []}
        }
        result = await log_repo.search(page=1, size=10)
        assert result["pages"] == 10  # ceil(95/10) = 10

    @pytest.mark.asyncio
    async def test_search_single_result_one_page(self, log_repo, mock_es):
        mock_es.search.return_value = {
            "hits": {
                "total": {"value": 1},
                "hits": [{"_id": "a", "_source": {"host": "x"}}],
            }
        }
        result = await log_repo.search(page=1, size=50)
        assert result["pages"] == 1


# =============================================================================
# Tests de count()
# =============================================================================

class TestCount:

    @pytest.mark.asyncio
    async def test_count_returns_integer(self, log_repo, mock_es):
        mock_es.count.return_value = {"count": 42}
        count = await log_repo.count()
        assert count == 42

    @pytest.mark.asyncio
    async def test_count_zero(self, log_repo, mock_es):
        mock_es.count.return_value = {"count": 0}
        count = await log_repo.count()
        assert count == 0

    @pytest.mark.asyncio
    async def test_count_with_custom_query(self, log_repo, mock_es):
        mock_es.count.return_value = {"count": 7}
        query = {"term": {"severity": "critical"}}
        count = await log_repo.count(query=query)
        assert count == 7
        mock_es.count.assert_called_once()


# =============================================================================
# Tests de delete_older_than()
# =============================================================================

class TestDeleteOlderThan:

    @pytest.mark.asyncio
    async def test_delete_returns_count(self, log_repo, mock_es):
        mock_es.delete_by_query.return_value = {"deleted": 15}
        deleted = await log_repo.delete_older_than(30)
        assert deleted == 15

    @pytest.mark.asyncio
    async def test_delete_zero_when_nothing_to_delete(self, log_repo, mock_es):
        mock_es.delete_by_query.return_value = {"deleted": 0}
        deleted = await log_repo.delete_older_than(365)
        assert deleted == 0

    @pytest.mark.asyncio
    async def test_delete_passes_correct_days(self, log_repo, mock_es):
        mock_es.delete_by_query.return_value = {"deleted": 5}
        await log_repo.delete_older_than(90)
        call_kwargs = mock_es.delete_by_query.call_args
        body = call_kwargs[1].get("body") or (call_kwargs[0][1] if len(call_kwargs[0]) > 1 else None)
        # Vérifier que "90d" apparaît dans la requête
        assert body is not None
        range_val = body["query"]["range"]["timestamp"]["lte"]
        assert "90d" in range_val

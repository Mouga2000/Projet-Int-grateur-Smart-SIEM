# app/tests/test_api/test_logs.py
# -------------------------------
# Tests unitaires des endpoints /api/v1/logs
# (Elasticsearch mocké)

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import Request

from app.repositories.log_repo import LogRepository


@pytest.fixture
def mock_es():
    es = AsyncMock()
    return es


@pytest.fixture
def log_repo(mock_es):
    repo = LogRepository(mock_es)
    repo.index_prefix = "siem-logs"
    return repo


@pytest.fixture
def sample_log():
    return {
        "timestamp": "2026-06-27T10:00:00Z",
        "source_ip": "192.168.1.10",
        "host": "server-01",
        "severity": "critical",
        "log_type": "auth",
        "raw_message": "Failed password for admin from 10.0.0.5",
        "tags": ["critical", "auth", "ip_mentioned"],
    }


class TestLogIngest:
    @pytest.mark.asyncio
    async def test_ingest_normalizes_and_indexes(self, log_repo, mock_es, sample_log):
        mock_es.index.return_value = {"_id": "abc123", "result": "created"}
        with patch(
            "app.services.normalization.NormalizationService.normalize",
            return_value=sample_log,
        ):
            result = await log_repo.ingest(sample_log.copy())
            assert result["id"] == "abc123"
            assert result["severity"] == "critical"

    @pytest.mark.asyncio
    async def test_ingest_calls_es_index(self, log_repo, mock_es, sample_log):
        mock_es.index.return_value = {"_id": "xyz789"}
        await log_repo.ingest(sample_log.copy())
        mock_es.index.assert_called_once()


class TestLogSearch:
    @pytest.mark.asyncio
    async def test_search_default_returns_all(self, log_repo, mock_es):
        mock_es.search.return_value = {
            "hits": {
                "total": {"value": 2},
                "hits": [
                    {"_id": "1", "_source": {"host": "srv1", "severity": "info"}},
                    {"_id": "2", "_source": {"host": "srv2", "severity": "error"}},
                ],
            }
        }
        result = await log_repo.search()
        assert result["total"] == 2
        assert len(result["items"]) == 2

    @pytest.mark.asyncio
    async def test_search_with_source_ip_filter(self, log_repo, mock_es):
        mock_es.search.return_value = {
            "hits": {
                "total": {"value": 1},
                "hits": [
                    {"_id": "1", "_source": {"source_ip": "10.0.0.1", "host": "srv1"}},
                ],
            }
        }
        query = {"term": {"source_ip": "10.0.0.1"}}
        result = await log_repo.search(query=query)
        assert result["total"] == 1

    @pytest.mark.asyncio
    async def test_search_pagination(self, log_repo, mock_es):
        mock_es.search.return_value = {"hits": {"total": {"value": 100}, "hits": []}}
        result = await log_repo.search(page=3, size=20)
        assert result["page"] == 3
        assert result["size"] == 20
        assert result["pages"] == 5


class TestLogGetById:
    @pytest.mark.asyncio
    async def test_get_by_id_returns_log(self, log_repo, mock_es):
        mock_es.get.return_value = {
            "_id": "abc123",
            "_source": {"host": "server-01", "raw_message": "test"},
        }
        result = await log_repo.get_by_id("abc123")
        assert result["id"] == "abc123"
        assert result["host"] == "server-01"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, log_repo, mock_es):
        from elasticsearch.exceptions import NotFoundError

        mock_es.get.side_effect = NotFoundError("not found", MagicMock(), {})
        result = await log_repo.get_by_id("nonexistent")
        assert result is None


class TestLogCount:
    @pytest.mark.asyncio
    async def test_count_returns_number(self, log_repo, mock_es):
        mock_es.count.return_value = {"count": 42}
        result = await log_repo.count()
        assert result == 42

    @pytest.mark.asyncio
    async def test_count_with_filter(self, log_repo, mock_es):
        mock_es.count.return_value = {"count": 7}
        result = await log_repo.count({"term": {"severity": "critical"}})
        assert result == 7


class TestLogDelete:
    @pytest.mark.asyncio
    async def test_delete_older_than_returns_count(self, log_repo, mock_es):
        mock_es.delete_by_query.return_value = {"deleted": 15}
        result = await log_repo.delete_older_than(90)
        assert result == 15

    @pytest.mark.asyncio
    async def test_delete_older_than_zero(self, log_repo, mock_es):
        mock_es.delete_by_query.return_value = {"deleted": 0}
        result = await log_repo.delete_older_than(30)
        assert result == 0


class TestLogTimeline:
    @pytest.mark.asyncio
    async def test_search_timeline_returns_buckets(self, log_repo, mock_es):
        mock_es.search.return_value = {
            "aggregations": {
                "events_over_time": {
                    "buckets": [
                        {"key_as_string": "2026-06-27T10:00:00Z", "doc_count": 10},
                        {"key_as_string": "2026-06-27T11:00:00Z", "doc_count": 5},
                    ]
                },
                "total_count": {"value": 15},
            }
        }
        result = await log_repo.search_timeline(interval="1h")
        assert result["interval"] == "1h"
        assert len(result["timeline"]) == 2
        assert result["timeline"][0]["count"] == 10
        assert result["total"] == 15

    @pytest.mark.asyncio
    async def test_search_timeline_empty(self, log_repo, mock_es):
        mock_es.search.return_value = {
            "aggregations": {
                "events_over_time": {"buckets": []},
                "total_count": {"value": 0},
            }
        }
        result = await log_repo.search_timeline(interval="1h")
        assert result["timeline"] == []
        assert result["total"] == 0

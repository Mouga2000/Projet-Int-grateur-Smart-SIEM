# app/tests/test_repositories/test_rule_repo.py
# -------------------------------
# Tests unitaires du repository Rule (app/repositories/rule_repo.py)

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.repositories.rule_repo import RuleRepository


@pytest.fixture
def db_session():
    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def rule_repo(db_session):
    return RuleRepository(db_session)


class TestRuleCreate:
    @pytest.mark.asyncio
    async def test_create_minimal(self, rule_repo, db_session):
        from app.models.sql_models import Rule
        mock_rule = MagicMock(spec=Rule)
        mock_rule.id = 1
        mock_rule.name = "Test Rule"
        mock_rule.severity = "medium"
        mock_rule.created_at = datetime.now()
        db_session.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'id', 1))

        with patch("app.repositories.rule_repo.Rule", return_value=mock_rule):
            result = await rule_repo.create({"name": "Test Rule"})
            assert result["id"] == 1

    @pytest.mark.asyncio
    async def test_create_full(self, rule_repo, db_session):
        from app.models.sql_models import Rule
        mock_rule = MagicMock(spec=Rule)
        mock_rule.id = 2
        mock_rule.name = "Full Rule"
        mock_rule.severity = "critical"
        mock_rule.created_at = datetime.now()
        db_session.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'id', 2))

        data = {"name": "Full Rule", "rule_type": "threshold", "severity": "critical",
                "condition": {"field": "log_type", "value": "auth"}, "mitre_tactic": "TA0001"}
        with patch("app.repositories.rule_repo.Rule", return_value=mock_rule):
            result = await rule_repo.create(data)
            assert result["id"] == 2


class TestRuleGetEnabled:
    @pytest.mark.asyncio
    async def test_get_enabled_rules(self, rule_repo, db_session):
        from app.models.sql_models import Rule
        mock_rule = MagicMock(spec=Rule)
        mock_rule.id = 1
        mock_rule.name = "Active Rule"
        mock_rule.description = None
        mock_rule.rule_type = "threshold"
        mock_rule.enabled = True
        mock_rule.severity = "high"
        mock_rule.priority = 80
        mock_rule.condition = {"field": "test"}
        mock_rule.actions = {}
        mock_rule.mitre_tactic = None
        mock_rule.mitre_technique = None
        mock_rule.version = 1
        mock_rule.created_by = None
        mock_rule.created_at = datetime.now()

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [mock_rule]
        db_session.execute.return_value = result_mock

        rules = await rule_repo.get_enabled_rules()
        assert len(rules) == 1
        assert rules[0]["name"] == "Active Rule"

    @pytest.mark.asyncio
    async def test_get_enabled_empty(self, rule_repo, db_session):
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        db_session.execute.return_value = result_mock
        rules = await rule_repo.get_enabled_rules()
        assert rules == []


class TestRuleGetById:
    @pytest.mark.asyncio
    async def test_get_existing(self, rule_repo, db_session):
        from app.models.sql_models import Rule
        mock_rule = MagicMock(spec=Rule)
        mock_rule.id = 1
        mock_rule.name = "Test"
        mock_rule.created_at = datetime.now()

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_rule
        db_session.execute.return_value = result_mock

        rule = await rule_repo.get_by_id(1)
        assert rule is not None
        assert rule["name"] == "Test"

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, rule_repo, db_session):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        db_session.execute.return_value = result_mock
        rule = await rule_repo.get_by_id(999)
        assert rule is None


class TestRuleUpdate:
    @pytest.mark.asyncio
    async def test_update(self, rule_repo, db_session):
        from app.models.sql_models import Rule
        mock_rule = MagicMock(spec=Rule)
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_rule
        db_session.execute.return_value = result_mock

        result = await rule_repo.update(1, {"enabled": False})
        assert result is True
        assert mock_rule.enabled is False

    @pytest.mark.asyncio
    async def test_update_nonexistent(self, rule_repo, db_session):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        db_session.execute.return_value = result_mock
        result = await rule_repo.update(999, {"enabled": False})
        assert result is False


class TestRuleDelete:
    @pytest.mark.asyncio
    async def test_soft_delete(self, rule_repo, db_session):
        from app.models.sql_models import Rule
        mock_rule = MagicMock(spec=Rule)
        mock_rule.deleted_at = None
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_rule
        db_session.execute.return_value = result_mock

        result = await rule_repo.delete(1)
        assert result is True
        assert mock_rule.deleted_at is not None

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, rule_repo, db_session):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        db_session.execute.return_value = result_mock
        result = await rule_repo.delete(999)
        assert result is False

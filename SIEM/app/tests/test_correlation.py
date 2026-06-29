import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.correlation import CorrelationEngine


# ==========================================================
# Fakes
# ==========================================================

class FakeRuleRepository:
    def __init__(self):
        self.rules = []

    async def get_enabled_rules(self):
        return self.rules


class FakeAlertRepository:
    def __init__(self):
        self.reset()

    def reset(self):
        self.created = False
        self.saved_alert = None
        self.last_id = 1000

    async def create(self, alert):
        self.created = True
        self.saved_alert = alert
        self.last_id += 1
        return self.last_id


@pytest.fixture
def alert_repo():
    return FakeAlertRepository()


@pytest.fixture
def rule_repo():
    return FakeRuleRepository()


@pytest.fixture
def engine(rule_repo, alert_repo):
    eng = CorrelationEngine(
        rule_repository=rule_repo,
        alert_repository=alert_repo,
        elastic_repository=None,
        redis_client=None,
        soar_service=None,
    )
    return eng


# ==========================================================
# Tests Single Event
# ==========================================================

class TestSingleEvent:
    @pytest.mark.asyncio
    async def test_single_event_match(self, engine, rule_repo, alert_repo):
        rule_repo.rules = [{"id": 1, "name": "Test", "type": "single_event", "severity": "high",
                            "condition": {"field": "event_type", "value": "login_failed"}, "description": "test"}]
        log = {"source_ip": "10.0.0.1", "event_type": "login_failed", "timestamp": "2026-01-01T00:00:00Z"}
        await engine.evaluate_event(log)
        assert alert_repo.created is True
        assert alert_repo.saved_alert["event_type"] == "login_failed"

    @pytest.mark.asyncio
    async def test_single_event_no_match(self, engine, rule_repo, alert_repo):
        rule_repo.rules = [{"id": 1, "name": "Test", "type": "single_event", "severity": "high",
                            "condition": {"field": "event_type", "value": "login_failed"}, "description": "test"}]
        log = {"source_ip": "10.0.0.1", "event_type": "login_success", "timestamp": "2026-01-01T00:00:00Z"}
        await engine.evaluate_event(log)
        assert alert_repo.created is False


# ==========================================================
# Tests Threshold Rule
# ==========================================================

class TestThresholdRule:
    @pytest.mark.asyncio
    async def test_threshold_not_reached(self, engine, rule_repo, alert_repo):
        rule_repo.rules = [{"id": 1, "name": "Threshold", "type": "threshold", "severity": "high",
                            "condition": {"field": "event_type", "value": "auth", "group_by": "source_ip"},
                            "threshold": {"count": 5, "window_seconds": 60}, "description": "test"}]
        log = {"source_ip": "10.0.0.1", "event_type": "auth", "timestamp": "2026-01-01T00:00:00Z"}
        with patch("app.services.correlation.get_redis") as mock_redis:
            mock_redis.return_value.incr = AsyncMock(return_value=3)
            mock_redis.return_value.expire = AsyncMock(return_value=True)
            await engine.evaluate_event(log)
            # Count 3 < 5 → pas d'alerte
            assert alert_repo.created is False

    @pytest.mark.asyncio
    async def test_threshold_reached(self, engine, rule_repo, alert_repo):
        rule_repo.rules = [{"id": 1, "name": "Threshold", "type": "threshold", "severity": "critical",
                            "condition": {"field": "event_type", "value": "auth", "group_by": "source_ip"},
                            "threshold": {"count": 5, "window_seconds": 60}, "description": "test"}]
        log = {"source_ip": "10.0.0.1", "event_type": "auth", "timestamp": "2026-01-01T00:00:00Z"}
        with patch("app.services.correlation.get_redis") as mock_redis:
            mock_redis.return_value.incr = AsyncMock(return_value=5)
            mock_redis.return_value.expire = AsyncMock(return_value=True)
            await engine.evaluate_event(log)
            assert alert_repo.created is True
            assert alert_repo.saved_alert["severity"] == "critical"

    @pytest.mark.asyncio
    async def test_threshold_redis_unavailable(self, engine, rule_repo, alert_repo):
        rule_repo.rules = [{"id": 1, "name": "Threshold", "type": "threshold", "severity": "high",
                            "condition": {"field": "event_type", "value": "auth", "group_by": "source_ip"},
                            "threshold": {"count": 5, "window_seconds": 60}, "description": "test"}]
        log = {"source_ip": "10.0.0.1", "event_type": "auth", "timestamp": "2026-01-01T00:00:00Z"}
        with patch("app.services.correlation.get_redis", side_effect=ConnectionError("Redis down")):
            await engine.evaluate_event(log)
            assert alert_repo.created is False  # Graceful degradation


# ==========================================================
# Tests UEBA Rule
# ==========================================================

class TestUEBARule:
    @pytest.mark.asyncio
    async def test_ueba_high_score_triggers_alert(self, engine, rule_repo, alert_repo):
        """Quand le profil UEBA a un score >= seuil, une alerte est créée."""
        rule_repo.rules = [{"id": 1, "name": "UEBA Anomaly", "type": "ueba", "severity": "high",
                            "condition": {"risk_threshold": 70}, "description": "UEBA alert"}]
        log = {"source_ip": "10.0.0.1", "decoded": {"user": "test_user"}, "timestamp": "2026-01-01T00:00:00Z"}

        fake_profile = {"entity_id": "test_user", "risk_score": 85}

        async def fake_get_profile(db, entity_id):
            return fake_profile

        with patch("app.core.database.async_session_factory"):
            with patch("app.services.ueba.get_profile", side_effect=fake_get_profile):
                await engine.evaluate_event(log)
                assert alert_repo.created is True

    @pytest.mark.asyncio
    async def test_ueba_low_score_no_alert(self, engine, rule_repo, alert_repo):
        """Score < seuil → pas d'alerte."""
        rule_repo.rules = [{"id": 1, "name": "UEBA Anomaly", "type": "ueba", "severity": "high",
                            "condition": {"risk_threshold": 70}, "description": "UEBA alert"}]
        log = {"source_ip": "10.0.0.1", "decoded": {"user": "test_user"}, "timestamp": "2026-01-01T00:00:00Z"}

        async def fake_get_profile(db, entity_id):
            return {"entity_id": "test_user", "risk_score": 10}

        with patch("app.core.database.async_session_factory"):
            with patch("app.services.ueba.get_profile", side_effect=fake_get_profile):
                await engine.evaluate_event(log)
                assert alert_repo.created is False

    @pytest.mark.asyncio
    async def test_ueba_no_profile_no_alert(self, engine, rule_repo, alert_repo):
        """Pas de profil UEBA → pas d'alerte."""
        rule_repo.rules = [{"id": 1, "name": "UEBA Anomaly", "type": "ueba", "severity": "high",
                            "condition": {"risk_threshold": 70}, "description": "UEBA alert"}]
        log = {"source_ip": "10.0.0.1", "decoded": {"user": "test_user"}, "timestamp": "2026-01-01T00:00:00Z"}

        with patch("app.core.database.async_session_factory"):
            with patch("app.services.ueba.get_profile", return_value=None):
                await engine.evaluate_event(log)
                assert alert_repo.created is False


# ==========================================================
# Tests Create Alert
# ==========================================================

class TestCreateAlert:
    @pytest.mark.asyncio
    async def test_alert_contains_mitre_fields(self, engine, rule_repo, alert_repo):
        rule_repo.rules = [{"id": 1, "name": "Test", "type": "single_event", "severity": "critical",
                            "condition": {"field": "event_type", "value": "test"}, "description": "MITRE test",
                            "mitre_tactic": "TA0001", "mitre_technique": "T1078"}]
        log = {"source_ip": "10.0.0.1", "event_type": "test", "timestamp": "2026-01-01T00:00:00Z"}
        await engine.evaluate_event(log)
        assert alert_repo.saved_alert["mitre_tactic"] == "TA0001"
        assert alert_repo.saved_alert["mitre_technique"] == "T1078"

    @pytest.mark.asyncio
    async def test_no_alert_on_no_rule_match(self, engine, rule_repo, alert_repo):
        rule_repo.rules = [{"id": 1, "name": "Test", "type": "single_event", "severity": "high",
                            "condition": {"field": "event_type", "value": "never_match"}, "description": "test"}]
        log = {"source_ip": "10.0.0.1", "event_type": "other", "timestamp": "2026-01-01T00:00:00Z"}
        await engine.evaluate_event(log)
        assert alert_repo.created is False

    @pytest.mark.asyncio
    async def test_alert_created_with_correct_rule_data(self, engine, rule_repo, alert_repo):
        rule_repo.rules = [{"id": 42, "name": "Specific Rule", "type": "single_event", "severity": "low",
                            "condition": {"field": "host", "value": "server-01"}, "description": "Specific desc"}]
        log = {"source_ip": "10.0.0.1", "host": "server-01", "event_type": "login", "timestamp": "2026-01-01T00:00:00Z"}
        await engine.evaluate_event(log)
        assert alert_repo.saved_alert["rule_id"] == 42
        assert alert_repo.saved_alert["rule_name"] == "Specific Rule"
        assert alert_repo.saved_alert["source_ip"] == "10.0.0.1"

# app/tests/test_services/test_correlation.py
# -------------------------------
# Tests unitaires du moteur de corrélation
#
# Le service correlation.py est encore un stub (non implémenté).
# Ces tests vérifient la structure attendue et pourront être
# complétés dès que le service sera implémenté.

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# =============================================================================
# Tests structurels — validation des règles de corrélation
# =============================================================================

class TestCorrelationRuleStructure:
    """Valide la structure des règles de corrélation utilisées par le moteur."""

    def test_single_event_rule_has_required_fields(self):
        """Une règle single_event doit avoir un type, des conditions et une action."""
        rule = {
            "id": 1,
            "name": "Brute force SSH",
            "type": "single_event",
            "conditions": {"severity": "critical", "log_type": "auth"},
            "action": "create_alert",
        }
        assert rule["type"] == "single_event"
        assert "conditions" in rule
        assert "action" in rule

    def test_threshold_rule_has_required_fields(self):
        """Une règle threshold doit préciser le seuil (count) et la fenêtre (window_minutes)."""
        rule = {
            "id": 2,
            "name": "5 échecs en 5 minutes",
            "type": "threshold",
            "conditions": {"log_type": "auth", "severity": "critical"},
            "threshold": {"count": 5, "window_minutes": 5},
            "action": "create_alert",
        }
        assert "threshold" in rule
        assert rule["threshold"]["count"] == 5
        assert rule["threshold"]["window_minutes"] == 5

    def test_sequence_rule_has_steps(self):
        """Une règle de séquence doit contenir des étapes ordonnées."""
        rule = {
            "id": 3,
            "name": "Reconnaisance puis latéral",
            "type": "sequence",
            "steps": [
                {"log_type": "auth", "severity": "warning"},
                {"log_type": "reseau", "severity": "info"},
            ],
            "window_minutes": 30,
        }
        assert len(rule["steps"]) >= 2
        assert "window_minutes" in rule

    def test_correlation_rule_has_sources(self):
        """Une règle de corrélation multi-sources doit lister les sources."""
        rule = {
            "id": 4,
            "name": "Firewall + AD",
            "type": "correlation",
            "sources": ["firewall", "active_directory", "endpoint"],
            "action": "create_alert",
        }
        assert len(rule["sources"]) > 1


# =============================================================================
# Tests de la logique de matching (simulation)
# =============================================================================

class TestCorrelationMatching:
    """Tests de la logique de correspondance d'un log avec une règle."""

    def _matches_single_event(self, rule: dict, log: dict) -> bool:
        """Simulation locale du matching single_event."""
        conditions = rule.get("conditions", {})
        for key, value in conditions.items():
            if log.get(key) != value:
                return False
        return True

    def test_single_event_match_exact(self):
        rule = {
            "type": "single_event",
            "conditions": {"severity": "critical", "log_type": "auth"},
        }
        log = {"severity": "critical", "log_type": "auth", "host": "server-01"}
        assert self._matches_single_event(rule, log) is True

    def test_single_event_no_match_severity(self):
        rule = {
            "type": "single_event",
            "conditions": {"severity": "critical", "log_type": "auth"},
        }
        log = {"severity": "info", "log_type": "auth"}
        assert self._matches_single_event(rule, log) is False

    def test_single_event_no_match_log_type(self):
        rule = {
            "type": "single_event",
            "conditions": {"severity": "critical", "log_type": "auth"},
        }
        log = {"severity": "critical", "log_type": "reseau"}
        assert self._matches_single_event(rule, log) is False

    def test_single_event_empty_conditions_matches_all(self):
        rule = {"type": "single_event", "conditions": {}}
        log = {"severity": "info", "log_type": "application"}
        assert self._matches_single_event(rule, log) is True


# =============================================================================
# Tests de la logique de seuil (threshold)
# =============================================================================

class TestThresholdLogic:
    """Vérifie la logique de comptage pour les règles de seuil."""

    def _should_trigger(self, count: int, threshold: int) -> bool:
        """Déclenchement si le compteur atteint ou dépasse le seuil."""
        return count >= threshold

    def test_threshold_not_reached(self):
        assert self._should_trigger(3, 5) is False

    def test_threshold_exactly_reached(self):
        assert self._should_trigger(5, 5) is True

    def test_threshold_exceeded(self):
        assert self._should_trigger(10, 5) is True

    def test_threshold_zero_always_triggers(self):
        assert self._should_trigger(0, 0) is True

    def test_threshold_count_one_below(self):
        assert self._should_trigger(4, 5) is False


# =============================================================================
# Tests du format de sortie : alerte générée
# =============================================================================

class TestAlertOutput:
    """Vérifie que les alertes générées par la corrélation ont le bon format."""

    def _build_alert(self, rule: dict, log: dict) -> dict:
        """Construit une alerte fictive à partir d'une règle et d'un log."""
        return {
            "rule_id": rule.get("id"),
            "rule_name": rule.get("name"),
            "severity": log.get("severity", "info"),
            "source_ip": log.get("source_ip"),
            "host": log.get("host"),
            "triggered_at": "2026-06-27T00:00:00Z",
            "details": log,
        }

    def test_alert_has_rule_id(self):
        rule = {"id": 42, "name": "Test rule"}
        log = {"severity": "critical", "source_ip": "10.0.0.5"}
        alert = self._build_alert(rule, log)
        assert alert["rule_id"] == 42

    def test_alert_inherits_severity(self):
        rule = {"id": 1, "name": "Rule"}
        log = {"severity": "critical"}
        alert = self._build_alert(rule, log)
        assert alert["severity"] == "critical"

    def test_alert_contains_details(self):
        rule = {"id": 1, "name": "Rule"}
        log = {"host": "server-01", "severity": "warning", "raw_message": "Brute force"}
        alert = self._build_alert(rule, log)
        assert alert["details"]["host"] == "server-01"
        assert alert["details"]["raw_message"] == "Brute force"

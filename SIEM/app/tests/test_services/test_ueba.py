# app/tests/test_services/test_ueba.py
# -------------------------------
# Tests unitaires du service UEBA (User and Entity Behavior Analytics)
#
# Le service ueba.py est encore un stub (non implémenté).
# Ces tests vérifient la logique comportementale attendue et pourront être
# complétés dès que le service sera implémenté.

import pytest
from datetime import datetime, timezone, timedelta


# =============================================================================
# Tests des règles heuristiques de détection d'anomalies
# =============================================================================

class TestAnomalouLoginHeuristics:
    """Vérifie les règles heuristiques pour détecter un login anormal."""

    def _is_outside_business_hours(self, hour: int) -> bool:
        """Connexion en dehors des heures ouvrées (8h-18h)."""
        return hour < 8 or hour >= 18

    def _is_new_ip(self, ip: str, known_ips: list) -> bool:
        """Vérifie si l'IP est inconnue pour cet utilisateur."""
        return ip not in known_ips

    def test_login_inside_business_hours(self):
        assert self._is_outside_business_hours(10) is False
        assert self._is_outside_business_hours(17) is False

    def test_login_outside_business_hours_night(self):
        assert self._is_outside_business_hours(2) is True
        assert self._is_outside_business_hours(23) is True

    def test_login_at_boundaries(self):
        assert self._is_outside_business_hours(8) is False  # Inclus
        assert self._is_outside_business_hours(18) is True   # Exclus

    def test_known_ip_not_anomalous(self):
        known = ["192.168.1.1", "10.0.0.5"]
        assert self._is_new_ip("192.168.1.1", known) is False

    def test_unknown_ip_is_anomalous(self):
        known = ["192.168.1.1", "10.0.0.5"]
        assert self._is_new_ip("203.0.113.42", known) is True

    def test_empty_known_ips_always_new(self):
        assert self._is_new_ip("192.168.1.1", []) is True


# =============================================================================
# Tests des features comportementales (feature engineering)
# =============================================================================

class TestUserBehaviorFeatures:
    """Vérifie l'extraction des features comportementales d'un utilisateur."""

    def _build_features(self, login_logs: list) -> dict:
        """Calcule les features de base d'un profil utilisateur."""
        if not login_logs:
            return {"login_count": 0, "unique_ips": 0, "avg_hour": None}

        hours = [log.get("hour", 12) for log in login_logs]
        ips = list({log.get("ip", "0.0.0.0") for log in login_logs})

        return {
            "login_count": len(login_logs),
            "unique_ips": len(ips),
            "avg_hour": sum(hours) / len(hours),
            "unique_ip_list": ips,
        }

    def test_empty_logs_returns_zero_counts(self):
        features = self._build_features([])
        assert features["login_count"] == 0
        assert features["unique_ips"] == 0

    def test_single_login_features(self):
        logs = [{"hour": 9, "ip": "192.168.1.1"}]
        features = self._build_features(logs)
        assert features["login_count"] == 1
        assert features["avg_hour"] == 9.0

    def test_multiple_logins_average_hour(self):
        logs = [
            {"hour": 8, "ip": "192.168.1.1"},
            {"hour": 12, "ip": "192.168.1.1"},
            {"hour": 16, "ip": "192.168.1.1"},
        ]
        features = self._build_features(logs)
        assert features["avg_hour"] == 12.0

    def test_deduplicated_ips(self):
        logs = [
            {"hour": 9, "ip": "192.168.1.1"},
            {"hour": 10, "ip": "192.168.1.1"},
            {"hour": 11, "ip": "10.0.0.5"},
        ]
        features = self._build_features(logs)
        assert features["unique_ips"] == 2


# =============================================================================
# Tests de la détection de mouvement latéral
# =============================================================================

class TestLateralMovementDetection:
    """Vérifie la logique de détection de mouvements latéraux."""

    def _detect_lateral_movement(self, logs: list, threshold_hosts: int = 3) -> bool:
        """
        Détecte un mouvement latéral si un même utilisateur
        accède à plus de N hôtes distincts dans une fenêtre temporelle.
        """
        if not logs:
            return False
        hosts_by_user: dict = {}
        for log in logs:
            user = log.get("user")
            host = log.get("host")
            if user and host:
                hosts_by_user.setdefault(user, set()).add(host)

        for user, hosts in hosts_by_user.items():
            if len(hosts) >= threshold_hosts:
                return True
        return False

    def test_no_logs_no_movement(self):
        assert self._detect_lateral_movement([]) is False

    def test_single_host_no_movement(self):
        logs = [
            {"user": "admin", "host": "server-01"},
            {"user": "admin", "host": "server-01"},
        ]
        assert self._detect_lateral_movement(logs, threshold_hosts=3) is False

    def test_two_hosts_below_threshold(self):
        logs = [
            {"user": "admin", "host": "server-01"},
            {"user": "admin", "host": "server-02"},
        ]
        assert self._detect_lateral_movement(logs, threshold_hosts=3) is False

    def test_three_hosts_triggers_detection(self):
        logs = [
            {"user": "admin", "host": "server-01"},
            {"user": "admin", "host": "server-02"},
            {"user": "admin", "host": "server-03"},
        ]
        assert self._detect_lateral_movement(logs, threshold_hosts=3) is True

    def test_different_users_no_trigger(self):
        """Chaque utilisateur accède à un seul hôte : pas de mouvement latéral."""
        logs = [
            {"user": "alice", "host": "server-01"},
            {"user": "bob", "host": "server-02"},
            {"user": "charlie", "host": "server-03"},
        ]
        assert self._detect_lateral_movement(logs, threshold_hosts=3) is False

    def test_missing_user_field_ignored(self):
        logs = [
            {"host": "server-01"},  # Pas d'utilisateur
            {"user": "admin", "host": "server-02"},
        ]
        assert self._detect_lateral_movement(logs, threshold_hosts=3) is False


# =============================================================================
# Tests de la détection d'exfiltration de données
# =============================================================================

class TestDataExfiltrationDetection:
    """Vérifie la logique de détection d'exfiltration de données."""

    def _detect_exfiltration(
        self, logs: list, volume_threshold_mb: int = 100
    ) -> bool:
        """
        Détecte une exfiltration si le volume total de données sortantes
        dépasse le seuil en Mo.
        """
        total = sum(log.get("bytes_out", 0) for log in logs) / (1024 * 1024)
        return total > volume_threshold_mb

    def test_small_volume_no_exfiltration(self):
        logs = [{"bytes_out": 1024 * 1024 * 10}]  # 10 Mo
        assert self._detect_exfiltration(logs, volume_threshold_mb=100) is False

    def test_large_volume_triggers_exfiltration(self):
        logs = [{"bytes_out": 1024 * 1024 * 150}]  # 150 Mo
        assert self._detect_exfiltration(logs, volume_threshold_mb=100) is True

    def test_cumulative_volume_triggers(self):
        logs = [
            {"bytes_out": 1024 * 1024 * 60},  # 60 Mo
            {"bytes_out": 1024 * 1024 * 60},  # 60 Mo → total 120 Mo
        ]
        assert self._detect_exfiltration(logs, volume_threshold_mb=100) is True

    def test_empty_logs_no_exfiltration(self):
        assert self._detect_exfiltration([]) is False

    def test_missing_bytes_out_treated_as_zero(self):
        logs = [{"host": "server-01"}]  # Pas de bytes_out
        assert self._detect_exfiltration(logs) is False


# =============================================================================
# Tests du score d'anomalie
# =============================================================================

class TestAnomalyScore:
    """Vérifie le calcul d'un score d'anomalie normalisé (0.0 - 1.0)."""

    def _compute_anomaly_score(self, indicators: list) -> float:
        """
        Score simple : proportion d'indicateurs positifs.
        Chaque indicateur est un bool (True = anomalie détectée).
        """
        if not indicators:
            return 0.0
        return sum(1 for i in indicators if i) / len(indicators)

    def test_no_indicators_score_zero(self):
        assert self._compute_anomaly_score([]) == 0.0

    def test_all_normal_score_zero(self):
        assert self._compute_anomaly_score([False, False, False]) == 0.0

    def test_all_anomalous_score_one(self):
        assert self._compute_anomaly_score([True, True, True]) == 1.0

    def test_half_anomalous_score_half(self):
        score = self._compute_anomaly_score([True, False, True, False])
        assert score == 0.5

    def test_score_between_zero_and_one(self):
        score = self._compute_anomaly_score([True, False, False, True, False])
        assert 0.0 <= score <= 1.0

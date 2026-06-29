# app/tests/test_services/test_ueba.py
# -------------------------------
# Tests unitaires du service UEBA (app/services/ueba.py)

import pytest
from unittest.mock import ANY
from app.services import ueba


class TestExtractFeatures:
    """Tests de l'extraction des features comportementales (9 dimensions)."""

    def test_empty_events_returns_empty_dict(self):
        assert ueba.extract_features([]) == {}

    def test_single_event_basic(self):
        events = [{"timestamp": "2026-06-29T10:00:00Z", "source_ip": "192.168.1.1",
                    "log_type": "auth", "severity": "info", "decoded": {"user": "admin"}}]
        feats = ueba.extract_features(events)
        assert feats["mean_hour"] == 10
        assert feats["total_events"] == 1
        assert feats["unique_ips"] == 1
        assert feats["unique_users"] == 1

    def test_multiple_events_compute_hour_stats(self):
        events = [
            {"timestamp": "2026-06-29T08:00:00Z", "source_ip": "192.168.1.1", "log_type": "auth", "severity": "info"},
            {"timestamp": "2026-06-29T12:00:00Z", "source_ip": "192.168.1.1", "log_type": "auth", "severity": "info"},
            {"timestamp": "2026-06-29T16:00:00Z", "source_ip": "10.0.0.5", "log_type": "reseau", "severity": "error"},
        ]
        feats = ueba.extract_features(events)
        assert feats["mean_hour"] == 12.0
        assert feats["total_events"] == 3
        assert feats["unique_ips"] == 2
        assert feats["unique_log_types"] == 2
        assert feats["error_ratio"] == pytest.approx(0.333, 0.01)
        assert feats["critical_ratio"] == 0.0

    def test_error_ratio_calculation(self):
        events = [
            {"timestamp": "2026-06-29T10:00:00Z", "source_ip": "1.2.3.4", "log_type": "auth", "severity": "error"},
            {"timestamp": "2026-06-29T11:00:00Z", "source_ip": "1.2.3.4", "log_type": "auth", "severity": "error"},
            {"timestamp": "2026-06-29T12:00:00Z", "source_ip": "1.2.3.4", "log_type": "auth", "severity": "info"},
        ]
        feats = ueba.extract_features(events)
        assert feats["error_ratio"] == pytest.approx(0.667, 0.01)
        assert feats["unique_ips"] == 1

    def test_user_from_decoded(self):
        events = [{"timestamp": "2026-06-29T10:00:00Z", "source_ip": "1.2.3.4", "log_type": "auth",
                    "severity": "info", "decoded": {"user": "admin"}}]
        feats = ueba.extract_features(events)
        assert feats["unique_users"] == 1

    def test_user_fallback_to_raw_data_uid(self):
        events = [{"timestamp": "2026-06-29T10:00:00Z", "source_ip": "1.2.3.4", "log_type": "auth",
                    "severity": "info", "raw_data": {"uid": "user123"}}]
        feats = ueba.extract_features(events)
        assert feats["unique_users"] == 1

    def test_bytes_feature(self):
        events = [{"timestamp": "2026-06-29T10:00:00Z", "source_ip": "1.2.3.4",
                    "log_type": "auth", "severity": "info", "bytes": 5000}]
        feats = ueba.extract_features(events)
        assert feats["avg_bytes"] == 5000.0

    def test_invalid_timestamp(self):
        events = [{"timestamp": "not-a-date", "source_ip": "1.2.3.4", "log_type": "auth", "severity": "info"}]
        feats = ueba.extract_features(events)
        assert "mean_hour" in feats

    def test_no_timestamp(self):
        events = [{"source_ip": "1.2.3.4", "log_type": "auth", "severity": "info"}]
        feats = ueba.extract_features(events)
        assert feats["mean_hour"] == 12.0

    def test_sample_events_capped_at_max(self):
        many_events = [{"timestamp": "2026-06-29T10:00:00Z", "source_ip": f"10.0.0.{i}",
                        "log_type": "auth", "severity": "info"} for i in range(100)]
        feats = ueba.extract_features(many_events, max_events=10)
        assert feats["total_events"] == 10


class TestFeaturesToVector:
    """Tests de conversion features → vecteur numérique."""

    def test_returns_ordered_list(self):
        feats = {"mean_hour": 10.0, "std_hour": 2.0, "total_events": 5, "unique_ips": 2,
                 "unique_users": 1, "unique_log_types": 3, "error_ratio": 0.5, "critical_ratio": 0.0, "avg_bytes": 100.0}
        vec = ueba.features_to_vector(feats)
        assert len(vec) == 9
        assert vec[0] == 10.0
        assert vec[4] == 1

    def test_missing_features_default_to_zero(self):
        vec = ueba.features_to_vector({})
        assert all(v == 0.0 for v in vec)
        assert len(vec) == 9

    def test_vector_order_matches_feature_names(self):
        feats = {k: float(i) for i, k in enumerate(ueba.FEATURE_NAMES)}
        vec = ueba.features_to_vector(feats)
        for i, name in enumerate(ueba.FEATURE_NAMES):
            assert vec[i] == float(i), f"Mismatch at {name}"


class TestComputeRiskScore:
    """Tests du calcul du score de risque (0-100)."""

    def test_no_model_returns_zero(self, monkeypatch):
        monkeypatch.setattr("os.path.exists", lambda _: False)
        score = ueba.compute_risk_score({"mean_hour": 10})
        assert score == 0

    def test_scores_are_capped_at_100(self, monkeypatch):
        import numpy as np
        mock_model = type("MockModel", (), {"predict": lambda self, x: np.array([-1])})()
        monkeypatch.setattr("os.path.exists", lambda _: True)
        monkeypatch.setattr("joblib.load", lambda _: mock_model)

        feats = {k: 0 for k in ueba.FEATURE_NAMES}
        feats["error_ratio"] = 0.8
        feats["critical_ratio"] = 0.5
        feats["unique_ips"] = 50
        feats["avg_bytes"] = 2_000_000
        score = ueba.compute_risk_score(feats)
        assert 0 <= score <= 100

    def test_business_rules_add_bonus(self, monkeypatch):
        import numpy as np
        mock_model = type("MockModel", (), {"predict": lambda self, x: np.array([1])})()
        monkeypatch.setattr("os.path.exists", lambda _: True)
        monkeypatch.setattr("joblib.load", lambda _: mock_model)

        feats = {k: 0 for k in ueba.FEATURE_NAMES}
        feats["error_ratio"] = 0.8
        score = ueba.compute_risk_score(feats)
        assert score == 25  # 10 base + 15 bonus erreurs

    def test_high_bytes_adds_bonus(self, monkeypatch):
        import numpy as np
        mock_model = type("MockModel", (), {"predict": lambda self, x: np.array([1])})()
        monkeypatch.setattr("os.path.exists", lambda _: True)
        monkeypatch.setattr("joblib.load", lambda _: mock_model)

        feats = {k: 0 for k in ueba.FEATURE_NAMES}
        feats["avg_bytes"] = 2_000_000
        score = ueba.compute_risk_score(feats)
        # 10 base + 15 (avg_bytes > 100k) + 25 (avg_bytes > 1M) = 50
        assert score == 50

    def test_model_anomaly_increases_score(self, monkeypatch):
        import numpy as np
        mock_model = type("MockModel", (), {"predict": lambda self, x: np.array([-1])})()
        monkeypatch.setattr("os.path.exists", lambda _: True)
        monkeypatch.setattr("joblib.load", lambda _: mock_model)

        feats = {k: 0 for k in ueba.FEATURE_NAMES}
        score = ueba.compute_risk_score(feats)
        assert score == 60  # 60 base (anomalie) + 0 bonus


class TestProfileDict:
    """Tests de conversion ProfilUEBA → dict."""

    def test_ueba_feature_names_are_complete(self):
        assert len(ueba.FEATURE_NAMES) == 9
        assert "mean_hour" in ueba.FEATURE_NAMES
        assert "avg_bytes" in ueba.FEATURE_NAMES

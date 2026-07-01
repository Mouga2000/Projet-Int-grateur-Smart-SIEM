# app/tests/conftest.py
# -------------------------------
# Fixtures pytest partagées

import pytest
from datetime import datetime, timezone
from app.main import app


@pytest.fixture(autouse=True)
def _clean_dependency_overrides():
    """Nettoie les overrides de dépendances après chaque test API."""
    yield
    if app.dependency_overrides:
        app.dependency_overrides.clear()


@pytest.fixture
def sample_log_minimal():
    """Un log minimal (juste le message)."""
    return {"raw_message": "Test event"}


@pytest.fixture
def sample_log_complete():
    """Un log complet au format SIEM."""
    return {
        "timestamp": datetime.now(timezone.utc),
        "source_ip": "192.168.1.10",
        "host": "server-01",
        "log_type": "auth",
        "severity": "error",
        "raw_message": "Failed password for admin from 10.0.0.5",
    }


@pytest.fixture
def sample_log_agent():
    """Un log au format agent."""
    return {
        "event_id": "test-uuid-123",
        "timestamp": "2026-06-24T15:29:56.602735+00:00",
        "agent_id": "AGENT-001",
        "hostname": "PC-SOPHIE",
        "operating_system": "Windows",
        "severity": "INFO",
        "collector": "LogsCollector",
        "event_type": "system_log",
        "message": "Port 3389 ouvert",
        "data": {"file": "test.log"},
    }


@pytest.fixture
def admin_user_dict():
    """Un utilisateur admin typique."""
    return {
        "id": 1,
        "username": "admin",
        "email": "admin@siem.local",
        "password_hash": "$2b$12$dummyhash",
        "role": "administrateur",
        "perimeter": [],
        "mfa_enabled": False,
        "mfa_secret": None,
        "is_active": True,
        "last_login": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

# app/tests/test_services/test_normalization.py
# -------------------------------
# Tests unitaires du pipeline de normalisation des logs

import pytest
from app.services.normalization import NormalizationService


# =============================================================================
# Tests de auto_tag()
# =============================================================================

class TestAutoTag:

    def test_failed_password_returns_critical_auth(self):
        result = NormalizationService.auto_tag("Failed password for admin from 10.0.0.5")
        assert result["severity"] == "critical"
        assert result["log_type"] == "auth"
        assert "critical" in result["tags"]
        assert "auth" in result["tags"]

    def test_invalid_user_returns_critical_auth(self):
        result = NormalizationService.auto_tag("Invalid user root from 192.168.1.1")
        assert result["severity"] == "critical"
        assert result["log_type"] == "auth"

    def test_authentication_failure_returns_critical_auth(self):
        result = NormalizationService.auto_tag("authentication failure for user admin")
        assert result["severity"] == "critical"
        assert result["log_type"] == "auth"

    def test_brute_force_returns_critical(self):
        result = NormalizationService.auto_tag("brute force attack detected from 10.0.0.5")
        assert result["severity"] == "critical"

    def test_error_message_returns_error(self):
        result = NormalizationService.auto_tag("Connection timeout to database")
        assert result["severity"] == "error"

    def test_traceback_returns_error(self):
        result = NormalizationService.auto_tag("Traceback (most recent call last)")
        assert result["severity"] == "error"

    def test_refused_returns_warning_auth(self):
        result = NormalizationService.auto_tag("Connection refused from 10.0.0.5")
        assert result["severity"] == "warning"
        assert result["log_type"] == "auth"

    def test_denied_returns_warning_auth(self):
        result = NormalizationService.auto_tag("Access denied for user admin")
        assert result["severity"] == "warning"
        assert result["log_type"] == "auth"

    def test_blocked_returns_warning_auth(self):
        result = NormalizationService.auto_tag("IP blocked after multiple attempts")
        assert result["severity"] == "warning"
        assert result["log_type"] == "auth"

    def test_forbidden_returns_warning_auth(self):
        result = NormalizationService.auto_tag("403 Forbidden access")
        assert result["severity"] == "warning"
        assert result["log_type"] == "auth"

    def test_warning_message_returns_warning(self):
        result = NormalizationService.auto_tag("Warning: disk space low")
        assert result["severity"] == "warning"

    def test_threshold_message_returns_warning(self):
        result = NormalizationService.auto_tag("Threshold exceeded for CPU usage")
        assert result["severity"] == "warning"

    def test_login_returns_info_auth(self):
        result = NormalizationService.auto_tag("User admin login successful")
        assert result["severity"] == "info"
        assert result["log_type"] == "auth"

    def test_logout_returns_info_auth(self):
        result = NormalizationService.auto_tag("User admin logged out")
        assert result["severity"] == "info"

    def test_session_returns_info_auth(self):
        result = NormalizationService.auto_tag("Session started for user admin")
        assert result["severity"] == "info"

    def test_network_connection_returns_info_reseau(self):
        result = NormalizationService.auto_tag("Connected to 192.168.1.1 port 443")
        assert result["log_type"] == "reseau"

    def test_disconnected_returns_info_reseau(self):
        result = NormalizationService.auto_tag("Disconnected from server")
        assert result["log_type"] == "reseau"

    def test_interface_returns_info_reseau(self):
        result = NormalizationService.auto_tag("Interface eth0 is up")
        assert result["log_type"] == "reseau"

    def test_service_started_returns_info_systeme(self):
        result = NormalizationService.auto_tag("Service nginx started")
        assert result["log_type"] == "systeme"

    def test_service_stopped_returns_info_systeme(self):
        result = NormalizationService.auto_tag("Service mysql stopped")
        assert result["log_type"] == "systeme"

    def test_process_returns_info_systeme(self):
        result = NormalizationService.auto_tag("Process apache2 restarted")
        assert result["log_type"] == "systeme"

    def test_default_message_returns_info_application(self):
        result = NormalizationService.auto_tag("Ceci est un message quelconque sans pattern")
        assert result["severity"] == "info"
        assert result["log_type"] == "application"

    def test_ip_mentioned_adds_tag(self):
        result = NormalizationService.auto_tag("Connexion from 192.168.1.100")
        assert "ip_mentioned" in result["tags"]

    def test_no_ip_does_not_add_tag(self):
        result = NormalizationService.auto_tag("Service started without IP")
        assert "ip_mentioned" not in result["tags"]

    def test_severity_override(self):
        """La sévérité fournie doit être surclassée par une règle plus haute."""
        result = NormalizationService.auto_tag("Failed password for admin", current_severity="info")
        assert result["severity"] == "critical"

    def test_empty_message_returns_defaults(self):
        result = NormalizationService.auto_tag("")
        assert result["severity"] == "info"
        assert result["log_type"] == "application"
        assert result["tags"] == ["info", "application"]

    def test_severity_less_restrictive_not_overridden(self):
        """Une sévérité existante 'critical' ne doit pas être diminuée par une règle 'info'."""
        result = NormalizationService.auto_tag("User admin logged in", current_severity="critical")
        assert result["severity"] == "critical"  # Ne doit pas être surclassé à "info"


# =============================================================================
# Tests de extract_structured()
# =============================================================================

class TestExtractStructured:

    def test_extract_ips(self):
        result = NormalizationService.extract_structured(
            "Attack from 192.168.1.100 and 10.0.0.5"
        )
        assert result["ips"] == ["192.168.1.100", "10.0.0.5"]

    def test_no_ip_returns_empty(self):
        result = NormalizationService.extract_structured("No IP here")
        assert result == {}

    def test_extract_mac_addresses_colon(self):
        result = NormalizationService.extract_structured(
            "MAC address AA:BB:CC:DD:EE:FF detected"
        )
        assert result["macs"] == ["AA:BB:CC:DD:EE:FF"]

    def test_extract_mac_addresses_hyphen(self):
        result = NormalizationService.extract_structured(
            "Device AA-BB-CC-DD-EE-FF connected"
        )
        assert result["macs"] == ["AA-BB-CC-DD-EE-FF"]

    def test_extract_user(self):
        result = NormalizationService.extract_structured(
            "user=admin failed login"
        )
        assert result["user"] == "admin"

    def test_extract_user_with_colon(self):
        result = NormalizationService.extract_structured(
            "user: sophie accessed"
        )
        assert result["user"] == "sophie"

    def test_extract_username_simple(self):
        result = NormalizationService.extract_structured(
            "user=john_doe connected"
        )
        assert result["user"] == "john_doe"

    def test_extract_ports(self):
        result = NormalizationService.extract_structured(
            "Connexion on port 22 and port 443"
        )
        assert result["ports"] == [22, 443]

    def test_extract_ports_as_integers(self):
        result = NormalizationService.extract_structured("port 8080")
        assert isinstance(result["ports"][0], int)

    def test_extract_all_together(self):
        result = NormalizationService.extract_structured(
            "Failed password for user=admin from 192.168.1.1 port 22, MAC AA:BB:CC:DD:EE:FF"
        )
        assert "ips" in result
        assert "user" in result
        assert "ports" in result
        assert "macs" in result
        assert result["user"] == "admin"
        assert 22 in result["ports"]
        assert "192.168.1.1" in result["ips"]

    def test_empty_message_returns_empty_dict(self):
        result = NormalizationService.extract_structured("")
        assert result == {}


# =============================================================================
# Tests de normalize()
# =============================================================================

class TestNormalize:

    @pytest.mark.asyncio
    async def test_normalize_complete_log(self):
        log = {
            "timestamp": "2026-06-24T10:00:00Z",
            "source_ip": "192.168.1.10",
            "host": "server-01",
            "log_type": "auth",
            "severity": "error",
            "raw_message": "Failed password for admin from 10.0.0.5",
        }
        result = await NormalizationService.normalize(log)
        assert result["source_ip"] == "192.168.1.10"
        assert result["host"] == "server-01"
        assert result["severity"] == "critical"
        assert result["log_type"] == "auth"
        assert "critical" in result["tags"]
        assert "ip_mentioned" in result["tags"]

    @pytest.mark.asyncio
    async def test_normalize_with_missing_fields(self):
        log = {"raw_message": "Service started"}
        result = await NormalizationService.normalize(log)
        assert result["host"] == "unknown"
        assert result["severity"] == "info"
        assert "timestamp" in result
        assert result["raw_message"] == "Service started"

    @pytest.mark.asyncio
    async def test_normalize_with_agent_format(self):
        log = {
            "hostname": "PC-SOPHIE",
            "event_type": "system_log",
            "severity": "INFO",
            "message": "Port 3389 ouvert",
            "agent_id": "AGENT-001",
        }
        result = await NormalizationService.normalize(log)
        assert result["host"] == "PC-SOPHIE"
        assert result["log_type"] == "system_log"
        assert result["raw_message"] == "Port 3389 ouvert"
        assert result["source_ip"] == "PC-SOPHIE"
        assert result["raw_data"]["agent_id"] == "AGENT-001"

    @pytest.mark.asyncio
    async def test_normalize_preserves_additional_data(self):
        log = {
            "message": "Test event",
            "hostname": "PC-01",
            "agent_id": "AGENT-01",
            "operating_system": "Windows",
            "collector": "LogCollector",
            "data": {"file": "test.log", "size": 1024},
        }
        result = await NormalizationService.normalize(log)
        assert result["raw_data"]["agent_id"] == "AGENT-01"
        assert result["raw_data"]["operating_system"] == "Windows"
        assert result["raw_data"]["collector"] == "LogCollector"
        assert result["raw_data"]["data"]["file"] == "test.log"

    @pytest.mark.asyncio
    async def test_normalize_empty_log(self):
        result = await NormalizationService.normalize({})
        assert result["host"] == "unknown"
        assert result["severity"] == "info"
        assert result["raw_message"] == ""
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_normalize_enrichment(self):
        log = {
            "message": "Failed password for user=root from 192.168.1.1 port 22",
        }
        result = await NormalizationService.normalize(log)
        assert result["decoded"]["user"] == "root"
        assert 22 in result["decoded"]["ports"]
        assert "192.168.1.1" in result["decoded"]["ips"]

    @pytest.mark.asyncio
    async def test_normalize_src_ip_fallback(self):
        log = {"src_ip": "10.0.0.1", "hostname": "server-01", "message": "test"}
        result = await NormalizationService.normalize(log)
        assert result["source_ip"] == "10.0.0.1"

    @pytest.mark.asyncio
    async def test_normalize_message_as_raw_message(self):
        log = {"message": "Raw log message"}
        result = await NormalizationService.normalize(log)
        assert result["raw_message"] == "Raw log message"

    @pytest.mark.asyncio
    async def test_normalize_prefers_raw_message(self):
        log = {"raw_message": "Use this", "message": "Ignore this"}
        result = await NormalizationService.normalize(log)
        assert result["raw_message"] == "Use this"

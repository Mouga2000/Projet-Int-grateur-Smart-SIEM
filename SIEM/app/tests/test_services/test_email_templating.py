# app/tests/test_services/test_email_templating.py
# -------------------------------
# Tests unitaires du service de templating email

from app.services.email_templating import render_alert_email, _html_escape


class TestRenderAlertEmail:
    """Tests du rendu du template d'email d'alerte."""

    def test_renders_alert_with_all_fields(self):
        alert = {
            "title": "Brute Force Detected",
            "rule_name": "Brute Force - 5 echecs",
            "severity": "critical",
            "source_ip": "192.168.1.100",
            "host": "server-01",
            "event_type": "auth",
            "description": "Multiple failed logins",
            "timestamp": "2026-06-29T10:30:00Z",
            "mitre_tactic": "credential_access",
            "mitre_technique": "T1110",
        }
        html = render_alert_email(alert)
        assert "<!DOCTYPE html>" in html
        assert "Brute Force Detected" in html
        assert "CRITICAL" in html
        assert "credential_access" in html
        assert "T1110" in html
        assert "192.168.1.100" in html
        assert "server-01" in html

    def test_renders_without_mitre(self):
        alert = {"title": "Simple Alert", "severity": "low", "source_ip": "10.0.0.1", "host": "test"}
        html = render_alert_email(alert)
        assert "Simple Alert" in html
        assert "LOW" in html

    def test_escapes_html_in_fields(self):
        alert = {"title": "<script>alert('xss')</script>", "severity": "high",
                 "source_ip": "1.2.3.4", "host": "test"}
        html = render_alert_email(alert)
        assert "&lt;script&gt;" in html
        assert "<script>" not in html

    def test_fallback_for_missing_template(self, monkeypatch):
        # Vider le cache et forcer l'absence de template
        monkeypatch.setattr("app.services.email_templating._load_template", lambda _: None)
        monkeypatch.setattr("app.services.email_templating._template_cache", {})
        alert = {"title": "Fallback Test", "severity": "high", "source_ip": "1.2.3.4",
                 "host": "test", "rule_name": "test", "description": "desc",
                 "mitre_tactic": "", "mitre_technique": ""}
        text = render_alert_email(alert)
        assert "ALERTE" in text or "Fallback" in text


class TestHtmlEscape:
    """Tests de l'échappement HTML."""

    def test_escapes_ampersand(self):
        assert _html_escape("a&b") == "a&amp;b"

    def test_escapes_angles(self):
        assert _html_escape("<tag>") == "&lt;tag&gt;"

    def test_escapes_quotes(self):
        assert _html_escape('say "hello"') == "say &quot;hello&quot;"

    def test_plain_text_unchanged(self):
        assert _html_escape("hello world") == "hello world"

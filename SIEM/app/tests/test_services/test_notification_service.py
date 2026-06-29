# app/tests/test_services/test_notification_service.py
# -------------------------------
# Tests unitaires du service de notification (app/services/notification_service.py)

import pytest
from unittest.mock import patch, MagicMock, ANY
from app.services.notification_service import NotificationService


class TestNotifyAlertCreated:
    """Tests de l'envoi de notification lors de la création d'une alerte."""

    def test_sends_in_app_to_analysts(self):
        alert = {"title": "Test Alert", "severity": "high", "source_ip": "10.0.0.5",
                 "host": "srv-01", "rule_name": "rule-1", "mitre_tactic": "TA0001", "mitre_technique": "T1078"}
        with patch("app.services.notification_service.send_in_app_notification.delay") as mock_inapp:
            NotificationService.notify_alert_created(alert, analyst_user_ids=[1, 2, 3])
            assert mock_inapp.call_count == 3
            mock_inapp.assert_any_call(1, "[HIGH] Test Alert", ANY)
            mock_inapp.assert_any_call(2, "[HIGH] Test Alert", ANY)
            mock_inapp.assert_any_call(3, "[HIGH] Test Alert", ANY)

    def test_no_in_app_when_no_analysts(self):
        alert = {"title": "Test", "severity": "low"}
        with patch("app.services.notification_service.send_in_app_notification.delay") as mock_inapp:
            NotificationService.notify_alert_created(alert, analyst_user_ids=[])
            mock_inapp.assert_not_called()

    def test_sends_email_if_smtp_configured(self, monkeypatch):
        monkeypatch.setattr("app.core.config.settings.SMTP_HOST", "smtp.test.com")
        alert = {"title": "Test", "severity": "high"}
        with patch("app.services.notification_service.send_email_notification.delay") as mock_email:
            NotificationService.notify_alert_created(alert, analyst_user_ids=[], admin_emails=["admin@test.com"])
            mock_email.assert_called_once()

    def test_no_email_if_smtp_not_configured(self, monkeypatch):
        monkeypatch.setattr("app.core.config.settings.SMTP_HOST", None)
        alert = {"title": "Test", "severity": "high"}
        with patch("app.services.notification_service.send_email_notification.delay") as mock_email:
            NotificationService.notify_alert_created(alert, analyst_user_ids=[], admin_emails=["admin@test.com"])
            mock_email.assert_not_called()

    def test_sends_slack_if_webhook_configured(self, monkeypatch):
        monkeypatch.setattr("app.core.config.settings.SLACK_WEBHOOK_URL", "https://hooks.slack.com/test")
        alert = {"title": "Test", "severity": "medium"}
        with patch("app.services.notification_service.send_slack_notification.delay") as mock_slack:
            NotificationService.notify_alert_created(alert, analyst_user_ids=[])
            mock_slack.assert_called_once()

    def test_format_severity_in_title(self):
        alert = {"title": "Brute Force", "severity": "critical"}
        with patch("app.services.notification_service.send_in_app_notification.delay") as mock_inapp:
            NotificationService.notify_alert_created(alert, analyst_user_ids=[1])
            title = mock_inapp.call_args[0][1]
            assert "[CRITICAL]" in title


class TestNotifyAlertEscalated:
    """Tests de notification d'escalade."""

    def test_sends_in_app_and_email(self, monkeypatch):
        monkeypatch.setattr("app.core.config.settings.SMTP_HOST", "smtp.test.com")
        alert = {"title": "Escalated Alert", "severity": "critical"}
        with patch("app.services.notification_service.send_in_app_notification.delay") as mock_inapp:
            with patch("app.services.notification_service.send_email_notification.delay") as mock_email:
                NotificationService.notify_alert_escalated(alert, admin_user_ids=[1, 2], admin_emails=["admin@test.com"])
                assert mock_inapp.call_count == 2
                mock_email.assert_called_once()

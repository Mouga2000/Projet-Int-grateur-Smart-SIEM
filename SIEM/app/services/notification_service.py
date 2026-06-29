# app/services/notification_service.py
# -------------------------------
# Service centralise d'envoi de notifications multi-canal

from typing import List, Optional

from app.core.config import settings
from app.tasks.notification_tasks import (
    send_email_notification,
    send_in_app_notification,
    send_slack_notification,
)


class NotificationService:
    """Envoie des notifications sur tous les canaux configures."""

    @staticmethod
    def notify_alert_created(
        alert: dict,
        analyst_user_ids: List[int],
        admin_emails: Optional[List[str]] = None,
    ):
        """
        Envoie une notification sur tous les canaux quand une alerte est creee.
        - In-app : pour tous les analystes
        - Email : si SMTP configure
        - Slack : si webhook configure
        """
        severity = alert.get("severity", "info").upper()
        title = f"[{severity}] {alert.get('title', 'Alerte SIEM')}"
        message = (
            f"Alerte de securite : {alert.get('title', 'N/A')}\n"
            f"Severite : {alert.get('severity', 'N/A')}\n"
            f"IP source : {alert.get('source_ip', 'N/A')}\n"
            f"Hote : {alert.get('host', 'N/A')}\n"
            f"Regle : {alert.get('rule_name', 'N/A')}\n"
            f"MITRE : {alert.get('mitre_tactic', 'N/A')} / {alert.get('mitre_technique', 'N/A')}"
        )

        # Canal in-app : pour tous les analystes
        for uid in analyst_user_ids:
            send_in_app_notification.delay(uid, title, message)

        # Canal email : si SMTP configure
        if settings.SMTP_HOST and admin_emails:
            for email in admin_emails:
                send_email_notification.delay(email, title, alert)

        # Canal Slack : si webhook configure
        if settings.SLACK_WEBHOOK_URL:
            send_slack_notification.delay("#security-alerts", message)

    @staticmethod
    def notify_alert_escalated(
        alert: dict,
        admin_user_ids: List[int],
        admin_emails: Optional[List[str]] = None,
    ):
        """Notification pour escalation d'alerte."""
        title = f"[ESCALADE] {alert.get('title', 'Alerte SIEM')}"
        message = (
            f"ESCALADE - {alert.get('title', 'N/A')}\n"
            f"Severite initiale : {alert.get('severity', 'N/A')}\n"
            f"IP : {alert.get('source_ip', 'N/A')}"
        )

        for uid in admin_user_ids:
            send_in_app_notification.delay(uid, title, message)

        if settings.SMTP_HOST and admin_emails:
            for email in admin_emails:
                send_email_notification.delay(email, title, alert)

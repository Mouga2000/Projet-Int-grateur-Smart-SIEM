# app/tasks/notification_tasks.py
# -------------------------------
# Tâches Celery pour les notifications
#
# Ce que tu dois mettre ici :
#
#   from app.tasks.celery import celery_app
#   from app.core.config import settings
#
#   @celery_app.task(bind=True, max_retries=3)
#   def send_email_notification(self, to: str, subject: str, body: str):
#       """Envoie un email via SMTP."""
#       pass
#
#   @celery_app.task(bind=True, max_retries=3)
#   def send_slack_notification(self, channel: str, message: str):
#       """Envoie une notification Slack via webhook."""
#       pass
#
#   @celery_app.task
#   def send_in_app_notification(user_id: int, title: str, message: str):
#       """Crée une notification en base de données."""
#       pass
#
#   @celery_app.task
#   def cleanup_old_logs(days: int = 90):
#       """Supprime les logs Elasticsearch plus vieux que N jours."""
#       pass

# app/tasks/celery.py
# -------------------------------
# Configuration Celery (broker Redis/RabbitMQ)
#
# Ce que tu dois mettre ici :
#
#   from celery import Celery
#   from app.core.config import settings
#
#   celery_app = Celery(
#       "smart_siem",
#       broker=settings.CELERY_BROKER_URL,
#       backend=settings.CELERY_RESULT_BACKEND,
#       include=[
#           "app.tasks.notification_tasks",
#           "app.tasks.soar_tasks",
#           "app.tasks.ueba_tasks",
#           "app.tasks.report_tasks",
#       ],
#   )
#
#   # Configuration optionnelle
#   celery_app.conf.update(
#       task_serializer="json",
#       accept_content=["json"],
#       result_serializer="json",
#       timezone="UTC",
#       enable_utc=True,
#       task_track_started=True,
#       task_soft_time_limit=300,  # 5 minutes
#       task_time_limit=600,       # 10 minutes
#       worker_max_tasks_per_child=1000,  # Évite les fuites mémoire
#   )
#
#   # --- Tâches périodiques (Celery Beat) ---
#   celery_app.conf.beat_schedule = {
#       # "cleanup-old-logs": {
#       #     "task": "app.tasks.notification_tasks.cleanup_old_logs",
#       #     "schedule": crontab(hour=3, minute=0),  # Tous les jours à 3h
#       # },
#       # "generate-daily-report": {
#       #     "task": "app.tasks.report_tasks.generate_daily_report",
#       #     "schedule": crontab(hour=6, minute=0),
#       # },
#       # "train-ueba-model": {
#       #     "task": "app.tasks.ueba_tasks.train_anomaly_model",
#       #     "schedule": crontab(hour=2, minute=0, day_of_week="monday"),
#       # },
#   }

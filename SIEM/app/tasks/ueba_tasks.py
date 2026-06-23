# app/tasks/ueba_tasks.py
# -------------------------------
# Tâches Celery pour l'analyse comportementale (UEBA)
#
# Ce que tu dois mettre ici :
#
#   from app.tasks.celery import celery_app
#
#   @celery_app.task(bind=True, soft_time_limit=3600)  # 1h max
#   def train_anomaly_model(self):
#       """Entraîne le modèle d'anomaly detection sur les données récentes."""
#       pass
#
#   @celery_app.task(bind=True, soft_time_limit=60)
#   def score_user_activity(self, user_id: int, recent_logs: list):
#       """Calcule un score d'anomalie pour un utilisateur."""
#       pass
#
#   @celery_app.task(bind=True)
#   def detect_lateral_movement_task(self, time_window_minutes: int = 60):
#       """Détection asynchrone des mouvements latéraux."""
#       pass
#
#   @celery_app.task(bind=True)
#   def detect_data_exfiltration_task(self, time_window_minutes: int = 60):
#       ""Détection asynchrone d'exfiltration de données."""
#       pass

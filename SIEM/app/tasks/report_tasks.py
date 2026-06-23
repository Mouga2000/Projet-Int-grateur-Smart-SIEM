# app/tasks/report_tasks.py
# -------------------------------
# Tâches Celery pour la génération de rapports
#
# Ce que tu dois mettre ici :
#
#   from app.tasks.celery import celery_app
#
#   @celery_app.task(bind=True, soft_time_limit=600)  # 10 min max
#   def generate_report_task(self, report_id: int):
#       """Génère un rapport PDF/CSV en arrière-plan."""
#       pass
#
#   @celery_app.task(bind=True, soft_time_limit=600)
#   def generate_daily_report(self):
#       """Génère le rapport quotidien automatique."""
#       pass
#
#   @celery_app.task(bind=True)
#   def export_search_results_task(self, query: dict, format: str = "csv"):
#       """Exporte les résultats de recherche dans un fichier."""
#       pass

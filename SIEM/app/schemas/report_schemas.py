# app/schemas/report_schemas.py
# -------------------------------
# Schémas Pydantic pour les rapports et statistiques
#
# Ce que tu dois mettre ici :
#
#   from pydantic import BaseModel, Field
#   from datetime import datetime
#   from typing import Optional
#
#   class ReportRequest(BaseModel):
#       title: str
#       description: Optional[str] = None
#       report_type: str = "summary"  # summary, detailed, compliance, custom
#       date_from: datetime
#       date_to: datetime
#       sources: list[str] = []
#       include_charts: bool = True
#       format: str = "pdf"  # pdf, csv, json
#       filters: dict = {}
#
#   class ReportResponse(BaseModel):
#       id: int
#       title: str
#       status: str  # pending, generating, completed, failed
#       format: str
#       file_url: Optional[str] = None
#       created_at: datetime
#       generated_at: Optional[datetime] = None
#
#   class DashboardStats(BaseModel):
#       total_logs_24h: int
#       total_alerts: int
#       alerts_by_severity: dict
#       alerts_by_status: dict
#       top_sources: list[dict]
#       top_attack_types: list[dict]
#       active_incidents: int
#       avg_response_time: Optional[float]  # Temps moyen de résolution (heures)
#       logs_over_time: list[dict]  # Séries temporelles
#
#   class ScheduledReport(BaseModel):
#       id: int
#       report_config: ReportRequest
#       cron_expression: str
#       recipients: list[str]
#       next_run: Optional[datetime]
#       last_run: Optional[datetime]

# app/core/config.py
# -------------------------------
# Configuration centralisée via pydantic-settings
#
# Ce que tu dois mettre ici :
#
#   from pydantic_settings import BaseSettings
#   from typing import Optional
#
#   class Settings(BaseSettings):
#       # --- Application ---
#       APP_NAME: str = "Smart SIEM"
#       APP_VERSION: str = "1.0.0"
#       APP_ENV: str = "development"
#       DEBUG: bool = True
#       SECRET_KEY: str
#
#       # --- Elasticsearch (base de données unique) ---
#       ELASTICSEARCH_HOST: str = "localhost"
#       ELASTICSEARCH_PORT: int = 9200
#       ELASTICSEARCH_SCHEME: str = "http"
#       ELASTICSEARCH_INDEX_USERS: str = "users"
#       ELASTICSEARCH_INDEX_AUDIT: str = "audit"
#       ELASTICSEARCH_INDEX_LOGS: str = "logs"
#       ELASTICSEARCH_INDEX_ALERTS: str = "alerts"
#       ELASTICSEARCH_INDEX_RULES: str = "rules"
#       ELASTICSEARCH_INDEX_PLAYBOOKS: str = "playbooks"
#       ELASTICSEARCH_INDEX_INCIDENTS: str = "incidents"
#       ELASTICSEARCH_INDEX_NOTIFICATIONS: str = "notifications"
#
#       # --- Redis / Celery ---
#       REDIS_HOST: str = "localhost"
#       REDIS_PORT: int = 6379
#       REDIS_PASSWORD: Optional[str] = None
#       CELERY_BROKER_URL: str = "redis://localhost:6379/0"
#       CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
#
#       # --- JWT ---
#       ALGORITHM: str = "HS256"
#       ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
#       REFRESH_TOKEN_EXPIRE_DAYS: int = 7
#
#       # --- Serveur ---
#       HOST: str = "0.0.0.0"
#       PORT: int = 8000
#       WORKERS: int = 4
#       LOG_LEVEL: str = "info"
#
#       # --- Collecte de logs ---
#       LOG_COLLECTOR_PORT: int = 514
#       LOG_COLLECTOR_PROTOCOL: str = "udp"
#       SYSLOG_ENABLED: bool = True
#
#       # --- Notifications ---
#       SMTP_HOST: Optional[str] = None
#       SMTP_PORT: Optional[int] = None
#       SMTP_USER: Optional[str] = None
#       SMTP_PASSWORD: Optional[str] = None
#       SLACK_WEBHOOK_URL: Optional[str] = None
#
#       # --- Machine Learning ---
#       ANOMALY_DETECTION_ENABLED: bool = True
#       ML_MODEL_PATH: str = "models/anomaly_detection.joblib"
#
#       model_config = {"env_file": ".env", "case_sensitive": True}
#
#   settings = Settings()
#
# Utilisation : from app.core.config import settings


from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # PostgreSQL (données structurées : utilisateurs, règles, audits…)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:0901@localhost:5432/SmartSiem"
    DATABASE_SYNC_URL: str = (
        "postgresql+psycopg2://postgres:0901@localhost:5432/SmartSiem"
    )

    # Elasticsearch (logs, alertes — données volumineuses)
    ELASTICSEARCH_HOST: str = "localhost"
    ELASTICSEARCH_PORT: int = 9200
    ELASTICSEARCH_SCHEME: str = "http"
    ELASTICSEARCH_INDEX_LOGS: str = "logs"

    # Redis / Celery
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Agent externe (clé API partagée pour l'ingestion automatique)
    AGENT_API_KEY: str = "siem-agent-key-2026"

    # --- Politique de rétention des données ---
    LOG_RETENTION_DAYS: int = 90  # 30, 90, 180 ou 365 jours
    AUDIT_RETENTION_DAYS: int = 365  # 1 an pour les audits

    class Config:
        env_file = ".env"


settings = Settings()

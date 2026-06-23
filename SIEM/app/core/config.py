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
#       APP_ENV: str = "development"  # development | staging | production
#       DEBUG: bool = True
#       SECRET_KEY: str
#       CORS_ORIGINS: str = "*"
#
#       # --- Base de données PostgreSQL ---
#       DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/siem"
#       DATABASE_SYNC_URL: str = "postgresql+psycopg2://user:pass@localhost:5432/siem"
#
#       # --- Elasticsearch ---
#       ELASTICSEARCH_HOSTS: str = "http://localhost:9200"
#       ELASTICSEARCH_USER: Optional[str] = None
#       ELASTICSEARCH_PASSWORD: Optional[str] = None
#
#       # --- Redis / Celery ---
#       REDIS_HOST: str = "localhost"
#       REDIS_PORT: int = 6379
#       REDIS_PASSWORD: Optional[str] = None
#       CELERY_BROKER_URL: str = "redis://localhost:6379/0"
#       CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
#
#       # --- Serveur ---
#       HOST: str = "0.0.0.0"
#       PORT: int = 8000
#       WORKERS: int = 4
#       LOG_LEVEL: str = "info"
#
#       # --- JWT ---
#       JWT_ALGORITHM: str = "HS256"
#       JWT_EXPIRATION_MINUTES: int = 60
#       JWT_REFRESH_EXPIRATION_DAYS: int = 7
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


from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Elasticsearch
    ELASTICSEARCH_HOST: str = "localhost"
    ELASTICSEARCH_PORT: int = 9200
    ELASTICSEARCH_SCHEME: str = "http"
    ELASTICSEARCH_INDEX_USERS: str = "users"
    ELASTICSEARCH_INDEX_AUDIT: str = "audit"
    
    class Config:
        env_file = ".env"

settings = Settings()
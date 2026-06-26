# ============================================================
# Smart SIEM - Dockerfile
# ============================================================
# Image Docker pour l'API FastAPI

FROM python:3.12-slim

LABEL maintainer="Smart SIEM Team" \
      description="Smart SIEM - Backend API"

# Variables d'environnement Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Répertoire de travail
WORKDIR /app

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY app/ ./app/

# Créer un utilisateur non-root (sécurité)
RUN useradd -m -u 1000 siem && chown -R siem:siem /app
USER siem

# Port exposé
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Commande de démarrage
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

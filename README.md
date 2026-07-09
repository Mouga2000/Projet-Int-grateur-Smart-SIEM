# Smart SIEM

Système de Gestion et d'Analyse des Événements de Sécurité (SIEM) avec orchestration SOAR et analyse comportementale (UEBA).

## Architecture

```
                         +------------------+
                         |   Frontend       |  React / Vite / Tailwind
                         | (Vercel ou local)|
                         +--------+---------+
                                  |  HTTPS / REST
                                  v
+--------------------------------+----------------------------------+
|                    API FastAPI (Port 8000)                        |
|  +----------+ +----------+ +----------+ +----------+ +---------+ |
|  |   Auth   | |   Logs   | |   Rules  | |  SOAR    | |  UEBA   | |
|  | JWT/MFA  | |   ES     | |  Engine  | | Playbook | |   ML    | |
|  +----------+ +----------+ +----------+ +----------+ +---------+ |
+--------------------------------+----------------------------------+
         |               |               |               |
         v               v               v               v
   +----------+    +----------+    +----------+    +-----------+
   |PostgreSQL|    |Elasticsearch|  |   Redis   |    |  Celery   |
   |:5432     |    |:9200       |  |:6379      |    | Worker    |
   +----------+    +----------+    +----------+    +-----------+
                                                       |
                                          +------------+------------+
                                          v            v            v
                                     +--------+  +--------+  +----------+
                                     |Archive |  |Report  |  |   UEBA   |
                                     |Tasks   |  |Tasks   |  |Training  |
                                     +--------+  +--------+  +----------+
```

## Stack technique

| Composant | Technologie |
|---|---|
| **Backend** | Python 3.12 / FastAPI |
| **Frontend** | React 19 / Vite / Tailwind CSS / Shadcn |
| **Base de données** | PostgreSQL (structure) + Elasticsearch (logs) |
| **Cache / Queue** | Redis + Celery |
| **ML** | Scikit-learn (Isolation Forest pour UEBA) |
| **Reverse proxy** | Traefik (production) |
| **Déploiement** | Docker Compose + VPS |

---

## Développement local

### 1. Backend (FastAPI)

```bash
cd SIEM

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer le .env (copier .env.example → .env)
cp .env.example .env

# Lancer le serveur
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

L'API est accessible sur `http://localhost:8000`.
La documentation interactive : `http://localhost:8000/docs`.

### 2. Backend avec Docker (Elasticsearch + Redis inclus)

```bash
# Démarrer les services
docker compose up -d elasticsearch redis api celery

# Logs
docker compose logs -f
```

### 3. Frontend

```bash
cd Frontend

npm install
npm run dev -- --host
```

Le frontend est accessible sur `http://localhost:5173`. Il appelle l'API sur `http://localhost:8000/api/v1` (configurable via `VITE_API_BASE_URL`).

### 4. Connexion Frontend ↔ Backend

Le CORS est configuré dans [SIEM/app/main.py](SIEM/app/main.py#L74-L84) :

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        # Ajouter l'URL de production si besoin
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Déploiement production (VPS + Traefik)

### Structure

```
/opt/apps/SmartSiem/Projet-Int-grateur-Smart-SIEM/
├── docker-compose.yml
├── .env
├── SIEM/
│   ├── Dockerfile
│   ├── app/
│   └── requirements.txt
└── Frontend/        # (déployé séparément sur Vercel)
```

### Services Docker

| Service | Rôle | Exposition |
|---|---|---|
| **Elasticsearch** | Stockage des logs | Interne (réseau internal) |
| **Redis** | Cache / Celery broker | Interne |
| **API** | FastAPI backend | Traefik → `api.smart-siem.domaine.com` |
| **Celery** | Tâches asynchrones | Interne |
| **Kibana** | Visualisation ES | Traefik → `kibana.smart-siem.domaine.com` |
| **PostgreSQL** | Base de données | Conteneur indépendant connecté au réseau |

### Déploiement

```bash
# 1. Cloner le projet
cd /opt/apps/SmartSiem
git clone <url> Projet-Int-grateur-Smart-SIEM

# 2. Créer le réseau Traefik (s'il n'existe pas)
docker network create traefik-net

# 3. Configurer le .env
cp SIEM/.env.example .env
nano .env  # Éditer les secrets

# 4. Connecter PostgreSQL au réseau internal
docker network connect smart-siem_internal postgres

# 5. Lancer la stack
docker compose up -d

# 6. Vérifier
docker compose ps
curl https://api.smart-siem.domaine.com/health
```

### Variables d'environnement (.env)

```env
DB_USER=postgres
DB_PASSWORD=changeme
SECRET_KEY=une-cle-aleatoire-tres-longue
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
FRONTEND_URL=https://smart-siem.vercel.app
LOG_RETENTION_DAYS=90
AUDIT_RETENTION_DAYS=365
ARCHIVE_ENABLED=True
ARCHIVE_AFTER_DAYS=90
```

### Commandes utiles

```bash
# Voir les logs
docker compose logs -f
docker compose logs api -f

# Rebuild et redémarrer après un git pull
git pull && docker compose up -d --build

# Arrêter
docker compose down

# Redémarrer un service spécifique
docker compose restart api
```

---

## Agents distants

Le dossier `Agents/` contient le logiciel à déployer sur les machines Windows/Linux à surveiller. Les agents envoient les logs à l'API via WebSocket ou HTTP.

---

## Fonctionnalités principales

- **Corrélation d'événements** : Règles de corrélation (single_event, threshold, correlation, sequence, UEBA)
- **SOAR** : Playbooks automatisés (blocage IP, désactivation utilisateur, notification Slack/Email)
- **UEBA** : Détection d'anomalies comportementales via Isolation Forest
- **MITRE ATT&CK** : Framework d'attaque intégré
- **Archivage** : Archivage des logs avec chaîne cryptographique (SHA-256 / Merkle)
- **Notifications** : Email (SMTP), Slack, notifications in-app
- **MFA** : Authentification multi-facteurs (TOTP)

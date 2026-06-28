# Smart SIEM — Backend

Plateforme SIEM (Security Information and Event Management) intelligente avec ingestion universelle de logs, normalisation automatique, investigations croisées, archivage conforme et orchestration SOAR.

Projet académique dans le cadre du cursus **UCAC ICAM — X3 PROJET INTÉGRATEUR**.

---

## Architecture

```
                    ┌─────────────┐
                    │   Clients   │
                    │  (UI/API)   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  FastAPI    │
                    │  (Uvicorn)  │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼───────┐  ┌───────▼───────┐  ┌───────▼───────┐
│   PostgreSQL   │  │ Elasticsearch │  │     Redis     │
│ (Utilisateurs, │  │  (Logs,       │  │  (Broker      │
│  Règles,       │  │   Indexes     │  │   Celery)     │
│  Audits,       │  │   journaliers)│  │               │
│  Investigations│  │               │  │               │
│  Archives)     │  │               │  │               │
└───────────────┘  └───────────────┘  └───────┬───────┘
                                              │
                                      ┌───────▼───────┐
                                      │    Celery     │
                                      │  (Beat + Workers)
                                      └───────────────┘
```

**Architecture duale :**
- **PostgreSQL** — données structurées : utilisateurs, règles, audits, investigations, archives
- **Elasticsearch** — données volumineuses : logs de sécurité (index `logs-YYYY-MM-DD`, rotation quotidienne)

---

## Stack technique

| Composant           | Technologie                          | Rôle                                        |
| ------------------- | ------------------------------------ | ------------------------------------------- |
| API                 | FastAPI 0.138 + Python 3.12+         | Serveur HTTP REST (Uvicorn)                 |
| Base de données     | PostgreSQL 17 + SQLAlchemy 2.0 async | Utilisateurs, règles, audits, investigations|
| Moteur de recherche | Elasticsearch 8.11                   | Logs, recherche plein texte, agrégations    |
| Cache & queue       | Redis + Celery                       | Broker tâches, purge automatique (Beat)     |
| Authentification    | JWT (HS256) + MFA (TOTP/pyotp)       | Sessions sécurisées et multi-facteurs       |
| Chiffrement         | cryptography (RSA 2048)              | Signatures archives, non-répudiation        |
| Migrations          | Alembic                              | Évolution du schéma PostgreSQL              |
| Tests               | pytest + pytest-asyncio + httpx      | Tests unitaires et API                      |
| Docker              | Docker Compose                       | Elasticsearch + Kibana + API conteneurisés  |

---

## Structure détaillée du projet

**Légende :** ✅ = implémenté | ⏳ = stub / à coder

```
SIEM/
│
├── .env                         # Variables d'environnement
├── .gitignore
├── .dockerignore
├── requirements.txt             # Dépendances Python
├── docker-compose.yml           # ✅ Elasticsearch + Kibana + API
├── Dockerfile                   # ✅ Image Docker de l'API
├── alembic.ini                  # Configuration migrations
├── README.md
│
├── certs/                       # Clé RSA auto-générée pour les archives
│   └── archive_key.pem          # ✅ Générée automatiquement au 1er archivage
│
├── data/
│   └── archives/                # ✅ Fichiers JSON compressés (archives certifiées)
│
├── app/                         # ———— CODE SOURCE PRINCIPAL ————
│   ├── main.py                  # ✅ Point d'entrée (lifespan, init_db, routers)
│   │
│   ├── core/                    # Configuration et connexions
│   │   ├── config.py            # ✅ Settings (JWT, PostgreSQL, ES, rétention, archivage)
│   │   ├── security.py          # ✅ Hash bcrypt, JWT, MFA/TOTP avec QR code
│   │   ├── elasticsearch.py     # ✅ Client ES singleton AsyncElasticsearch
│   │   ├── database.py          # ✅ SQLAlchemy async + init_db() (création auto des tables)
│   │   └── redis.py             # ⏳ Client Redis async (cache + rate limiting)
│   │
│   ├── api/                     # Couche API FastAPI
│   │   ├── dependencies.py      # ✅ get_current_user, require_role, require_permissions
│   │   ├── middleware.py        # ⏳ CORS, TrustedHost, logging, rate limiting (stub)
│   │   └── v1/                  # Routes API version 1
│   │       ├── router.py        # ✅ Routeur central (auth, users, logs, admin, archive, investigations)
│   │       ├── auth.py          # ✅ Login, logout, MFA (setup, verify, disable, status)
│   │       ├── users.py         # ✅ CRUD users + /setup + /{username}/role + /{username}/perimeter
│   │       ├── logs.py          # ✅ Ingest (universel), list, search, timeline, get, delete
│   │       ├── admin.py         # ✅ Purge logs/audit + GET /retention
│   │       ├── archive.py       # ✅ Créer/lister/chaîne/vérifier/exporter archives
│   │       ├── investigations.py# ✅ CRUD investigations + ajout logs + mise à jour statut
│   │       ├── health.py        # ⏳ GET /health, /ready, /live (stub)
│   │       ├── alerts.py        # ⏳ CRUD /alerts, acknowledge, escalate (stub)
│   │       ├── playbooks.py     # ⏳ CRUD /playbooks, POST /{id}/execute (stub)
│   │       ├── search.py        # ⏳ POST /search, GET /search/saved (stub)
│   │       └── reports.py       # ⏳ GET /reports/dashboard, POST /reports/generate (stub)
│   │
│   ├── models/                  # Modèles de données
│   │   ├── sql_models.py        # ✅ User, Rule, Playbook, Incident, Alert, ProfilUEBA,
│   │   │                        #    AuditLog, Notification, Archive, Investigation, InvestigationLog
│   │   ├── user.py              # ✅ Modèle User (Pydantic)
│   │   ├── log.py               # ✅ Modèle Log (Pydantic → document ES)
│   │   ├── alert.py             # ⏳ Alerte (Pydantic → ES)
│   │   ├── rule.py              # ⏳ Règle de corrélation
│   │   ├── playbook.py          # ⏳ Playbook SOAR
│   │   ├── incident.py          # ⏳ Incident
│   │   ├── notification.py      # ⏳ Notification
│   │   └── audit_log.py         # ⏳ Trace d'audit
│   │
│   ├── schemas/                 # Schémas Pydantic (validation API)
│   │   ├── user_schemas.py      # ✅ UserCreate, UserLogin, Token, UserResponse, UserUpdateRole
│   │   ├── log_schemas.py       # ✅ RawLog, LogCreate, LogResponse, LogSearchRequest, LogListResponse
│   │   ├── alert_schemas.py     # ⏳ AlertUpdate, AlertResponse, PlaybookCreate…
│   │   ├── search_schemas.py    # ⏳ SearchRequest, SearchResponse
│   │   └── report_schemas.py    # ⏳ ReportRequest, DashboardStats
│   │
│   ├── services/                # Logique métier
│   │   ├── auth.py              # ✅ AuthService (authenticate avec MFA, logout, audit)
│   │   ├── audit_service.py     # ✅ AuditService (login/logout/MFA/gestion)
│   │   ├── normalization.py     # ✅ Pipeline : auto_tag (7 règles regex), extract_structured
│   │   │                        #    (IP, MAC, user, port), normalize (format SIEM + Agent)
│   │   ├── archiver.py          # ✅ ArchiverService (SHA-256, Merkle tree, chaîne, signature RSA)
│   │   ├── correlation.py       # ⏳ Moteur de corrélation (threshold, séquence)
│   │   ├── ueba.py              # ⏳ Analyse comportementale (ML)
│   │   ├── soar.py              # ⏳ Orchestration SOAR (playbooks)
│   │   ├── alerts.py            # ⏳ Gestion des alertes
│   │   ├── search.py            # ⏳ Recherche Elasticsearch DSL
│   │   └── reports.py           # ⏳ Rapports PDF/CSV
│   │
│   ├── repositories/            # Pattern Repository (accès données)
│   │   ├── base.py              # ✅ CRUD générique PostgreSQL (SQLAlchemy)
│   │   ├── user_repo.py         # ✅ CRUD utilisateurs PostgreSQL
│   │   ├── audit_repo.py        # ✅ Audit logs PostgreSQL + purge par âge
│   │   ├── log_repo.py          # ✅ CRUD logs ES (ingest, bulk_ingest, search, timeline,
│   │   │                        #    get_by_id, delete, delete_older_than, search_by_date_range)
│   │   ├── archive_repo.py      # ✅ Archives PostgreSQL (create, list, get, chain, verify)
│   │   ├── investigation_repo.py# ✅ Investigations + InvestigationLog PostgreSQL
│   │   ├── alert_repo.py        # ⏳ Alertes (ES) — stub
│   │   ├── rule_repo.py         # ⏳ Règles (PostgreSQL) — stub
│   │   ├── playbook_repo.py     # ⏳ Playbooks (PostgreSQL) — stub
│   │   └── incident_repo.py     # ⏳ Incidents (PostgreSQL) — stub
│   │
│   ├── tasks/                   # Tâches asynchrones Celery
│   │   ├── celery.py            # ✅ Config Celery + Beat schedule (purge à 3h UTC)
│   │   ├── notification_tasks.py# ✅ purge_old_logs() (ES + PG), send_email/slack (stub)
│   │   ├── soar_tasks.py        # ⏳ Exécution playbooks, enrichissement
│   │   ├── ueba_tasks.py        # ⏳ Entraînement ML, scoring anomalies
│   │   └── report_tasks.py      # ⏳ Génération de rapports
│   │
│   ├── utils/                   # Fonctions utilitaires
│   │   ├── tags.py              # ✅ Enum Role (5 rôles) + Enum Perimeter (4 niveaux)
│   │   │                        #    + StatutIncident + NiveauAlerte + ROLE_PERMISSIONS_MAP
│   │   ├── logging.py           # ⏳ Configuration Loguru
│   │   ├── validators.py        # ⏳ Validation IP, domaine, hash…
│   │   └── mitre.py             # ⏳ Base MITRE ATT&CK
│   │
│   └── tests/                   # Tests
│       ├── conftest.py          # ✅ Fixtures partagées
│       ├── test_core_security.py# ✅ 18 tests : hash bcrypt, JWT, MFA TOTP
│       ├── test_schemas.py      # ✅ 17 tests : validation UserCreate, LogCreate, search
│       ├── test_utils_tags.py   # ✅ 17 tests : Role, Perimeter, permissions
│       ├── test_services/
│       │   ├── test_normalization.py  # ✅ 44 tests : auto_tag, extract_structured, normalize
│       │   └── test_auth_service.py   # ✅ Tests AuthService
│       └── test_api/
│           ├── test_auth.py     # ✅ Tests endpoints auth
│           ├── test_logs.py     # ✅ Tests endpoints logs
│           ├── test_alerts.py   # ✅ Tests endpoints alertes
│           └── test_search.py   # ✅ Tests recherche
│
├── migrations/                  # Migrations Alembic
│   ├── env.py                   # ✅ Configuration (import des modèles)
│   └── versions/                # Scripts de migration
│
└── scripts/                     # Scripts utilitaires
    ├── generate_dataset_ctu.py  # ⏳ Génération dataset de test
    ├── populate_test_data.py    # ⏳ Peuplement base de démo
    └── seed_rules.py            # ⏳ Initialisation règles de corrélation
```

---

## État d'avancement

### ✅ Implémenté et fonctionnel

**Colonne Auth :** « Public » = accès libre · « Token » = JWT requis · « Admin » = JWT + rôle administrateur

#### 🔐 Authentification & Utilisateurs

| Endpoint                                    | Méthode | Description                                          | Auth   |
| ------------------------------------------- | ------- | ---------------------------------------------------- | ------ |
| `POST /api/v1/auth/login`                   | POST    | Connexion (username/password + MFA optionnelle)      | Public |
| `POST /api/v1/auth/logout`                  | POST    | Déconnexion                                          | Token  |
| `GET  /api/v1/auth/mfa/status`              | GET     | Voir si la MFA est activée                           | Token  |
| `POST /api/v1/auth/mfa/setup`               | POST    | Générer le secret TOTP + QR code (base64)            | Token  |
| `POST /api/v1/auth/mfa/verify`              | POST    | Activer la MFA après vérification du code            | Token  |
| `POST /api/v1/auth/mfa/disable`             | POST    | Désactiver la MFA (confirmation mot de passe)        | Token  |
| `GET  /api/v1/users/`                       | GET     | Liste des utilisateurs                               | Admin  |
| `POST /api/v1/users/`                       | POST    | Créer un utilisateur                                 | Admin  |
| `PUT  /api/v1/users/{username}/role`        | PUT     | Modifier le rôle                                     | Admin  |
| `PUT  /api/v1/users/{username}/perimeter`   | PUT     | Modifier le périmètre                                | Admin  |
| `POST /api/v1/users/setup`                  | POST    | Bootstrap premier administrateur                     | Public |
| `GET  /api/v1/users/me`                     | GET     | Profil de l'utilisateur connecté                     | Token  |

#### 📥 Logs

| Endpoint                       | Méthode | Description                                                       | Auth   |
| ------------------------------ | ------- | ----------------------------------------------------------------- | ------ |
| `POST /api/v1/logs/ingest`     | POST    | Ingérer un log (format universel JSON, normalisation + tagging)   | Public |
| `GET  /api/v1/logs/`           | GET     | Liste paginée des logs (du plus récent au plus ancien)            | Token  |
| `POST /api/v1/logs/search`     | POST    | Recherche multi-critères (IP, host, type, sévérité, date, tags)  | Token  |
| `GET  /api/v1/logs/timeline`   | GET     | Série temporelle pour graphique (agrégation date_histogram ES)    | Token  |
| `GET  /api/v1/logs/{id}`       | GET     | Détail d'un log par ID Elasticsearch                              | Token  |
| `DELETE /api/v1/logs/{id}`     | DELETE  | Supprimer un log par ID Elasticsearch                             | Token  |

> **Endpoint `/timeline`** : retourne les comptages groupés par intervalle configurable (10s, 1m, 5m, 1h, 1d, 1w, 1M) avec filtres optionnels par date et sévérité.

#### 🔍 Investigations

| Endpoint                                         | Méthode | Description                                              | Auth     |
| ------------------------------------------------ | ------- | -------------------------------------------------------- | -------- |
| `POST /api/v1/investigations/`                   | POST    | Créer une investigation (titre, sévérité, tags, MITRE)  | Analyste |
| `GET  /api/v1/investigations/`                   | GET     | Lister les investigations (filtre par statut, pagination)| Token    |
| `GET  /api/v1/investigations/{id}`               | GET     | Détail d'une investigation avec ses logs associés        | Token    |
| `POST /api/v1/investigations/{id}/logs`          | POST    | Ajouter un log ES à une investigation avec note/verdict  | Analyste |
| `PATCH /api/v1/investigations/{id}/status`       | PATCH   | Mettre à jour le statut (ouverte→en_cours→resolue→classee)| Analyste|
| `PATCH /api/v1/investigations/{id}`              | PATCH   | Modifier titre, description, sévérité, tags, assignation | Analyste |

> **Verdicts log** : `suspect`, `benign`, `confirmed`, `false_positive`

#### 🛠️ Administration

| Endpoint                                    | Méthode | Description                              | Auth  |
| ------------------------------------------- | ------- | ---------------------------------------- | ----- |
| `POST /api/v1/admin/purge/logs`             | POST    | Purger les logs ES plus vieux que N jours | Admin |
| `POST /api/v1/admin/purge/audit`            | POST    | Purger les audits PG plus vieux que N jours| Admin |
| `GET  /api/v1/admin/retention`              | GET     | Afficher la configuration de rétention   | Admin |

#### 🗄️ Archivage certifié

| Endpoint                                        | Méthode | Description                                     | Auth  |
| ----------------------------------------------- | ------- | ----------------------------------------------- | ----- |
| `POST /api/v1/admin/archive/create`             | POST    | Créer une archive certifiée des logs             | Admin |
| `GET  /api/v1/admin/archive/list`               | GET     | Lister les archives avec pagination              | Admin |
| `GET  /api/v1/admin/archive/chain`              | GET     | Afficher la chaîne cryptographique               | Admin |
| `POST /api/v1/admin/archive/verify/{id}`        | POST    | Vérifier l'intégrité d'une archive (4 contrôles)| Admin |
| `GET  /api/v1/admin/archive/{id}`               | GET     | Détail d'une archive                             | Admin |
| `GET  /api/v1/admin/archive/{id}/export`        | GET     | Exporter les preuves pour audit réglementaire    | Admin |

---

### 🔑 Fonctionnalités implémentées — Détail

#### Sécurité & Authentification
- Hash bcrypt des mots de passe (sel unique par hash)
- Tokens JWT : `access_token` (30 min) + `refresh_token` (7 jours)
- MFA TOTP avec QR code base64 (pyotp + qrcode) — optionnelle, activable par utilisateur
- 5 rôles : `lecteur`, `analyste`, `auditeur`, `rssi`, `administrateur` (enum `Role`)
- 4 périmètres : `equipe`, `service`, `filiale`, `environnement` (enum `Perimeter`)
- RBAC avec matrice de permissions granulaires (`ROLE_PERMISSIONS_MAP`)
- Filtre automatique des logs par périmètre utilisateur dans les recherches
- Audit trail complet des actions sensibles (login, logout, MFA, gestion utilisateurs)

#### Normalisation des logs
- Pipeline universel : accepte tout JSON (`raw_message` ou `message`, `host` ou `hostname`)
- Tagging automatique par 7 règles regex (brute force → critical, error, warning, auth, réseau, système…)
- Extraction structurée : IPs, adresses MAC, utilisateurs, ports
- Mapping Agent → SIEM (`event_type`, `hostname`, `agent_id`, `collector`)
- Affichage console RAW → NORMALIZED pour le débogage

#### Investigations croisées
- Regroupement de logs Elasticsearch suspects sous une investigation commune
- Verdicts analytiques par log (suspect, benign, confirmed, false_positive)
- Notes d'analyse par événement
- Mapping MITRE ATT&CK (tactic + technique) par investigation
- Statuts de cycle de vie : ouverte → en_cours → resolue → classee
- Assignation à un analyste

#### Archivage conforme (réglementaire)
- Extraction ES par plage de dates + compression gzip
- SHA-256 du fichier d'archive (streaming pour gros fichiers)
- Merkle tree sur les logs individuels (vérification granulaire)
- Chaîne de hachage blockchain-like entre archives successives
- Signature RSA 2048 bits de l'horodatage (non-répudiation)
- 4 vérifications d'intégrité : existence fichier, SHA-256, chaîne, signature

#### Infrastructure & Données
- Création automatique des tables PostgreSQL au démarrage (`init_db`)
- Rotation quotidienne des index ES (`logs-YYYY-MM-DD`)
- Politique de rétention configurable : logs 90j, audits 365j
- Purge automatique quotidienne à 3h UTC via Celery Beat
- Soft-delete sur les modèles User, Rule, Playbook
- Timestamps automatiques (`created_at`, `updated_at`) via mixins SQLAlchemy

---

### ⏳ En cours / À faire

| Module                        | Priorité | Description                              |
| ----------------------------- | -------- | ---------------------------------------- |
| **Middleware (CORS, logs)**    | Haute    | Activer CORSMiddleware + logging requêtes|
| **Alertes**                   | Haute    | CRUD + workflow (acquittement, escalade) |
| **Règles de corrélation**     | Haute    | Moteur de détection sur flux de logs     |
| **Health Check**              | Haute    | GET /health (ES ping, DB ping)           |
| **Playbooks SOAR**            | Moyenne  | Automatisation des réponses aux alertes  |
| **Rapports**                  | Moyenne  | Dashboard stats + génération PDF/CSV     |
| **UEBA**                      | Basse    | Analyse comportementale (ML/scoring)     |
| **Celery workers**            | Basse    | Tâches email/Slack/UEBA/rapports         |
| **Redis client**              | Basse    | Cache + rate limiting                    |

---

## Modèles de données (PostgreSQL)

| Table              | Description                                              |
| ------------------ | -------------------------------------------------------- |
| `users`            | Utilisateurs, rôles, périmètres, MFA                    |
| `rules`            | Règles de corrélation (type, condition JSON, MITRE)      |
| `playbooks`        | Playbooks SOAR (étapes JSON, triggers, variables)        |
| `incidents`        | Regroupements d'alertes avec timeline                    |
| `alertes`          | Alertes de sécurité (niveau, score confiance, MITRE)     |
| `profils_ueba`     | Profils comportementaux (baseline, risk_score)           |
| `audit_logs`       | Traces d'actions sensibles (action, IP, résultat)        |
| `notifications`    | Notifications in-app / email / Slack / SMS               |
| `archives`         | Archives certifiées (SHA-256, Merkle, chaîne, signature) |
| `investigations`   | Investigations de sécurité (MITRE, statut, assignation)  |
| `investigation_logs`| Lien log ES ↔ investigation (note, verdict analyste)   |

---

## Installation

### Prérequis

- **Python 3.12+**
- **PostgreSQL 17+** (données structurées)
- **Elasticsearch 8.x** (logs)
- **Redis 7+** (broker Celery)

### Installation locale

```bash
# 1. Cloner le dépôt
git clone <url-du-repo>
cd SIEM

# 2. Créer et activer l'environnement virtuel
python -m venv venv
.\venv\Scripts\Activate    # Windows
# source venv/bin/activate  # Linux/macOS

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
# Copier .env et renseigner les valeurs (SECRET_KEY, DATABASE_URL, etc.)

# 5. Lancer Elasticsearch (Docker)
docker run -d --name es \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0

# 6. S'assurer que PostgreSQL tourne et que la base SmartSiem existe
# CREATE DATABASE "SmartSiem";

# 7. Lancer l'API (tables créées automatiquement)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 8. Créer le premier administrateur (bootstrap)
curl -X POST http://localhost:8000/api/v1/users/setup \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "email": "admin@siem.local", "password": "admin123!", "role": "lecteur", "perimeter": []}'
```

> Les tables PostgreSQL sont créées **automatiquement** au démarrage via `init_db()` dans `app/core/database.py`.

### Variables d'environnement (`.env`)

| Variable                | Défaut                                | Description                         |
| ----------------------- | ------------------------------------- | ------------------------------------ |
| `SECRET_KEY`            | *(obligatoire)*                       | Clé secrète JWT                      |
| `ALGORITHM`             | `HS256`                               | Algorithme JWT                       |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30`                          | Durée token d'accès                  |
| `DATABASE_URL`          | `postgresql+asyncpg://…/SmartSiem`   | URL PostgreSQL async                 |
| `ELASTICSEARCH_HOST`    | `localhost`                           | Hôte Elasticsearch                   |
| `ELASTICSEARCH_PORT`    | `9200`                                | Port Elasticsearch                   |
| `REDIS_HOST`            | `localhost`                           | Hôte Redis                           |
| `CELERY_BROKER_URL`     | `redis://localhost:6379/0`            | Broker Celery                        |
| `LOG_RETENTION_DAYS`    | `90`                                  | Rétention des logs (jours)           |
| `AUDIT_RETENTION_DAYS`  | `365`                                 | Rétention des audits (jours)         |
| `ARCHIVE_ENABLED`       | `True`                                | Activer l'archivage certifié         |
| `ARCHIVE_DIR`           | `data/archives`                       | Répertoire des archives              |
| `ARCHIVE_AFTER_DAYS`    | `90`                                  | Âge minimum pour archiver            |
| `AGENT_API_KEY`         | `siem-agent-key-2026`                 | Clé API pour les agents externes     |

### Déploiement Docker

```bash
# Démarrer Elasticsearch + Kibana + API
docker-compose up -d

# Kibana disponible sur http://localhost:5601
# API disponible sur http://localhost:8000
# Docs Swagger sur http://localhost:8000/docs
```

> **Note :** PostgreSQL tourne sur l'hôte (hors Docker). L'API accède via `host.docker.internal`.

### Lancer le worker Celery

```bash
# Worker + Beat (tâches périodiques)
celery -A app.tasks.celery.celery_app worker --loglevel=info
celery -A app.tasks.celery.celery_app beat --loglevel=info
```

---

## Tests

```bash
# Exécuter tous les tests
pytest -v

# Avec rapport de couverture
pytest --cov=app --cov-report=term-missing

# Tests par module
pytest app/tests/test_core_security.py -v       # Sécurité (hash, JWT, MFA)
pytest app/tests/test_schemas.py -v             # Schémas Pydantic
pytest app/tests/test_utils_tags.py -v          # Rôles et permissions
pytest app/tests/test_services/test_normalization.py -v  # Normalisation logs
pytest app/tests/test_services/test_auth_service.py -v   # AuthService
pytest app/tests/test_api/ -v                   # Endpoints API
```

### Couverture des tests

| Module                                       | Tests  | Couverture                                       |
| -------------------------------------------- | ------ | ------------------------------------------------ |
| Normalisation (auto_tag, extract, normalize) | 44     | ✅ Toutes les règles, format agent, cas limites  |
| Sécurité (hash, JWT, MFA)                    | 18     | ✅ Bcrypt, tokens, TOTP                          |
| Schémas (validation Pydantic)                | 17     | ✅ UserCreate, LogCreate, search                 |
| Utilitaires (Role, Perimeter)                | 17     | ✅ 5 rôles, 4 périmètres, permissions           |
| AuthService                                  | ✅     | Authenticate, logout, audit                      |
| API (auth, logs, alertes, search)            | ✅     | Tests endpoints httpx                            |

---

## Ingestion de logs (format agent)

L'endpoint `POST /api/v1/logs/ingest` accepte tout JSON sans authentification.

**Format SIEM classique :**
```json
{
  "source_ip": "192.168.1.10",
  "host": "srv-web-01",
  "raw_message": "Failed password for invalid user admin from 192.168.1.10 port 22 ssh2",
  "severity": "critical"
}
```

**Format agent universel :**
```json
{
  "hostname": "workstation-42",
  "event_type": "auth",
  "message": "Authentication failure for user bob from 10.0.0.5",
  "agent_id": "agent-001",
  "operating_system": "Windows 11",
  "collector": "winlogbeat"
}
```

Le pipeline de normalisation gère automatiquement les deux formats et extrait IPs, MACs, utilisateurs et ports.

---

## Contribution

1. Créer une branche (`git checkout -b feature/ma-fonctionnalite`)
2. Respecter la structure et les patterns existants (Repository Pattern, services séparés)
3. Exécuter les tests (`pytest`)
4. Formatter le code (`black . && isort .`)
5. Ouvrir une Pull Request

---

## Licence

Projet académique — **UCAC ICAM - X3 PROJET INTÉGRATEUR**.

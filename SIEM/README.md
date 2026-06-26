# Smart SIEM — Backend

Plateforme SIEM (Security Information and Event Management) intelligente avec corrélation d'événements, analyse comportementale (UEBA) et orchestration SOAR.

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
│ (Utilisateurs, │  │  (Logs,       │  │  (Cache,      │
│  Règles,       │  │   Alertes)    │  │   Queue)      │
│  Audits,       │  │               │  │               │
│  Incidents)    │  │               │  │               │
└───────────────┘  └───────────────┘  └───────┬───────┘
                                              │
                                      ┌───────▼───────┐
                                      │    Celery     │
                                      │  (Workers)    │
                                      └───────────────┘
```

## Stack technique

| Composant           | Technologie                          | Rôle                                       |
| ------------------- | ------------------------------------ | ------------------------------------------- |
| API                 | FastAPI (Python 3.12+)               | Serveur HTTP REST (Uvicorn)                 |
| Base de données    | PostgreSQL 17 + SQLAlchemy 2.0 async | Utilisateurs, règles, audits, incidents    |
| Moteur de recherche | Elasticsearch 8.x                    | Logs, alertes, recherche plein texte        |
| Cache & queue       | Redis + Celery                       | Cache, files d'attente, tâches asynchrones |
| Authentification    | JWT + MFA (TOTP)                     | Sessions sécurisées et multi-facteurs     |
| Migrations          | Alembic                              | Évolution du schéma PostgreSQL            |
| Tests               | pytest + pytest-asyncio + httpx      | 104 tests unitaires                         |

> **Architecture duale :** PostgreSQL stocke les données structurées (utilisateurs, règles, audits). Elasticsearch stocke les logs et les alertes (données volumineuses, recherche plein texte).

## Structure détaillée du projet

**Légende :** ✅ = implémenté | ⏳ = en commentaire (à coder)

```
SIEM/
│
├── .env                         # Variables d'environnement
├── .gitignore                   # Fichiers/dossiers exclus de Git
├── requirements.txt             # Dépendances Python
├── docker-compose.yml           # Orchestration Docker
├── Dockerfile.api               # Image Docker de l'API
├── Dockerfile.worker            # Image Docker du worker Celery
├── alembic.ini                  # Configuration migrations
├── README.md                    # Cette documentation
│
├── app/                         # ———— CODE SOURCE PRINCIPAL ————
│   ├── main.py                  # ✅ Point d'entrée (lifespan, init_db, routers)
│   │
│   ├── core/                    # Configuration et connexions
│   │   ├── config.py            # ✅ Settings (JWT, PostgreSQL, ES, clé agent)
│   │   ├── security.py          # ✅ Hash bcrypt, JWT, MFA/TOTP avec QR code
│   │   ├── elasticsearch.py     # ✅ Client ES singleton AsyncElasticsearch
│   │   ├── database.py          # ✅ SQLAlchemy async + init_db() (création auto des tables)
│   │   └── redis.py             # ⏳ Client Redis async (cache + rate limiting)
│   │
│   ├── api/                     # Couche API FastAPI
│   │   ├── dependencies.py      # ✅ get_current_user (PG), require_role, require_permissions
│   │   ├── middleware.py        # ⏳ CORS, TrustedHost, logging, rate limiting
│   │   └── v1/                  # Routes API version 1
│   │       ├── auth.py          # ✅ Login, logout, MFA (setup, verify, disable, status)
│   │       ├── users.py         # ✅ CRUD users + /setup + /{username}/role + /{username}/perimeter
│   │       ├── logs.py          # ✅ POST /logs/ingest (format universel), GET /logs, POST /search
│   │       ├── router.py        # ✅ Routeur central (auth, users, logs actifs)
│   │       ├── health.py        # ⏳ GET /health, /ready, /live
│   │       ├── search.py        # ⏳ POST /search, GET /search/saved
│   │       ├── alerts.py        # ⏳ CRUD /alerts, acknowledge, escalate
│   │       ├── playbooks.py     # ⏳ CRUD /playbooks, POST /{id}/execute
│   │       └── reports.py       # ⏳ GET /reports/dashboard, POST /reports/generate
│   │
│   ├── models/                  # Modèles de données
│   │   ├── sql_models.py        # ✅ Modèles SQLAlchemy : User, Rule, Playbook, Incident, AuditLog, Notification
│   │   ├── user.py              # ✅ Modèle User (Pydantic — validation)
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
│   │   ├── log_schemas.py       # ✅ RawLog, LogCreate, LogResponse, LogSearchRequest
│   │   ├── alert_schemas.py     # ⏳ AlertUpdate, AlertResponse, PlaybookCreate…
│   │   ├── search_schemas.py    # ⏳ SearchRequest, SearchResponse
│   │   └── report_schemas.py    # ⏳ ReportRequest, DashboardStats
│   │
│   ├── services/                # Logique métier
│   │   ├── auth.py              # ✅ AuthService (authenticate avec MFA, logout, audit)
│   │   ├── audit_service.py     # ✅ AuditService (login/logout/MFA/gestion)
│   │   ├── normalization.py     # ✅ Pipeline : auto_tag (10 règles), extract_structured (IP, MAC, user, port), normalize
│   │   ├── correlation.py       # ⏳ Moteur de corrélation (threshold, séquence)
│   │   ├── ueba.py              # ⏳ Analyse comportementale (ML)
│   │   ├── soar.py              # ⏳ Orchestration SOAR (playbooks)
│   │   ├── alerts.py            # ⏳ Gestion des alertes
│   │   ├── search.py            # ⏳ Recherche Elasticsearch DSL
│   │   └── reports.py           # ⏳ Rapports PDF/CSV
│   │
│   ├── repositories/            # Pattern Repository
│   │   ├── base.py              # ✅ CRUD générique PostgreSQL (SQLAlchemy)
│   │   ├── user_repo.py         # ✅ CRUD utilisateurs PostgreSQL
│   │   ├── audit_repo.py        # ✅ Audit logs PostgreSQL
│   │   ├── log_repo.py          # ✅ CRUD logs Elasticsearch (ingest, search, get_by_id, delete)
│   │   ├── alert_repo.py        # ⏳ Alertes (ES)
│   │   ├── rule_repo.py         # ⏳ Règles (PG)
│   │   ├── playbook_repo.py     # ⏳ Playbooks (PG)
│   │   └── incident_repo.py     # ⏳ Incidents (PG)
│   │
│   ├── tasks/                   # Tâches asynchrones Celery
│   │   ├── celery.py            # ⏳ Configuration Celery
│   │   ├── notification_tasks.py# ⏳ Envoi emails, Slack, nettoyage logs
│   │   ├── soar_tasks.py        # ⏳ Exécution playbooks, enrichissement
│   │   ├── ueba_tasks.py        # ⏳ Entraînement ML, scoring anomalies
│   │   └── report_tasks.py      # ⏳ Génération de rapports
│   │
│   ├── utils/                   # Fonctions utilitaires
│   │   ├── tags.py              # ✅ Enum Role (5 rôles) + Enum Perimeter (4 niveaux) + permissions
│   │   ├── logging.py           # ⏳ Configuration Loguru
│   │   ├── validators.py        # ⏳ Validation IP, domaine, hash…
│   │   └── mitre.py             # ⏳ Base MITRE ATT&CK
│   │
│   └── tests/                   # Tests unitaires
│       ├── conftest.py          # ✅ Fixtures partagées
│       ├── test_core_security.py# ✅ 18 tests : hash, JWT, MFA
│       ├── test_schemas.py      # ✅ 17 tests : validation UserCreate, LogCreate, search
│       ├── test_utils_tags.py   # ✅ 17 tests : Role, Perimeter, permissions
│       ├── test_services/
│       │   └── test_normalization.py # ✅ 44 tests : auto_tag, extract_structured, normalize
│       ├── test_api/            # ⏳ Tests endpoints
│       └── test_repositories/   # ⏳ Tests repositories
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

## État d'avancement

### ✅ Implémenté

**Colonne Auth :** « Public » = accès libre · « Token » = token JWT requis · « Admin » = token JWT + rôle administrateur requis

#### 🔐 Authentification & Utilisateurs

| Endpoint                                    | Méthode | Description                                         | Auth   |
| ------------------------------------------- | -------- | --------------------------------------------------- | ------ |
| `POST /api/v1/auth/login`                 | POST     | Connexion (username/password + MFA optionnelle)     | Public |
| `POST /api/v1/auth/logout`                | POST     | Déconnexion                                        | Token  |
| `GET  /api/v1/auth/mfa/status`            | GET      | Voir si la MFA est activée                         | Token  |
| `POST /api/v1/auth/mfa/setup`             | POST     | Générer le secret TOTP + QR code                  | Token  |
| `POST /api/v1/auth/mfa/verify`            | POST     | Activer la MFA après vérification du code         | Token  |
| `POST /api/v1/auth/mfa/disable`           | POST     | Désactiver la MFA (avec confirmation mot de passe) | Token  |
| `GET  /api/v1/users/`                     | GET      | Liste des utilisateurs                              | Admin  |
| `POST /api/v1/users/`                     | POST     | Créer un utilisateur                               | Admin  |
| `PUT  /api/v1/users/{username}/role`      | PUT      | Modifier le rôle                                   | Admin  |
| `PUT  /api/v1/users/{username}/perimeter` | PUT      | Modifier le périmètre                             | Admin  |
| `POST /api/v1/users/setup`                | POST     | Bootstrap premier admin                             | Public |
| `GET  /api/v1/users/me`                   | GET      | Profil de l'utilisateur connecté                   | Token  |

#### 📥 Logs

| Endpoint                     | Méthode | Description                                                      | Auth   |
| ---------------------------- | -------- | ---------------------------------------------------------------- | ------ |
| `POST /api/v1/logs/ingest` | POST     | Ingérer un log (format universel, normalisation + tagging + ES) | Public |
| `GET  /api/v1/logs/`<br /> | GET      | Liste paginée des logs                                          | Token  |
| `POST /api/v1/logs/search` | POST     | Recherche avancée (filtres, dates, sources)                     | Token  |
| `GET  /api/v1/logs/{id}`   | GET      | Détail d'un log par ID ES                                       | Token  |
| `DELETE /api/v1/logs/{id}` | DELETE   | Supprimer un log                                                 | Token  |

**Fonctionnalités :**

- Hash bcrypt des mots de passe
- Tokens JWT (access + refresh)
- MFA TOTP avec QR code (optionnelle, activable par utilisateur)
- 5 rôles : `lecteur`, `analyste`, `auditeur`, `rssi`, `administrateur` (enum `Role`)
- 4 périmètres fonctionnels : `equipe`, `service`, `filiale`, `environnement` (enum `Perimeter`)
- RBAC avec permissions granulaires (`ROLE_PERMISSIONS_MAP`)
- Normalisation universelle des logs : tagging auto (10 règles), extraction IP/MAC/user/port
- Affichage console RAW -> NORMALIZED pour le débogage
- Création automatique des tables PostgreSQL au démarrage (`init_db`)
- Architecture duale : PostgreSQL (users, rules, audits) + ES (logs)

### ⏳ En cours / À faire

| Module                            | Priorité | Description                              |
| --------------------------------- | --------- | ---------------------------------------- |
| **Alertes**                 | Haute     | CRUD + workflow (acquittement, escalade) |
| **Règles de corrélation** | Haute     | Moteur de détection sur les logs        |
| **Playbooks SOAR**          | Moyenne   | Automatisation des réponses             |
| **Rapports**                | Moyenne   | Dashboard stats + génération PDF/CSV   |
| **UEBA**                    | Basse     | Analyse comportementale (ML)             |
| **Tasks Celery**            | Basse     | Tâches asynchrones                      |
| **Tests API**               | Haute     | Tests des endpoints avec httpx           |

## Installation

### Récupérer le projet

```bash
# Cloner le dépôt
git clone <url-du-repo>
cd SIEM

# Voir les branches disponibles
git branch -a

# Travailler sur une branche spécifique (ex: SIEM)
git checkout SIEM
```

### Prérequis

- **Python 3.12+**
- **PostgreSQL 17+** (utilisateurs, règles, audits)
- **Elasticsearch 8.x** (logs)
- **Redis 7+** (pour Celery, optionnel)

### Étapes

# 2. Créer et activer l'environnement virtuel

python -m venv venv
.\venv\Scripts\Activate    # Windows

# 3. Installer les dépendances

pip install -r requirements.txt

# 4. Configurer les variables d'environnement dans .env

# SECRET_KEY, DATABASE_URL, ELASTICSEARCH_HOST, etc.

# 5. Démarrer les services

# PostgreSQL : s'assurer que le service tourne et que la base SmartSiem existe

# Elasticsearch : docker run -d --name es -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" docker.elastic.co/elasticsearch/elasticsearch:8.11.0

# 6. Lancer l'API (les tables sont créées automatiquement)

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 7. Créer le premier administrateur (bootstrap)

curl -X POST http://localhost:8000/api/v1/users/setup 
  -H "Content-Type: application/json" 
  -d '{"username": "admin", "email": "admin@siem.local", "password": "admin123!", "role": "lecteur", "perimeter": []}'

```

> Les tables PostgreSQL sont créées **automatiquement** au démarrage via `init_db()` dans `app/core/database.py`.

### Bases de données

| Base | Technologie | Contenu |
|---|---|---|
| `SmartSiem` (PostgreSQL) | SQLAlchemy async | utilisateurs, règles, playbooks, incidents, audits, notifications |
| `localhost:9200` (Elasticsearch) | AsyncElasticsearch | logs (index `logs-YYYY-MM-DD`) |

### Lancer le serveur pour l'agent

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

L'agent envoie les logs sur `POST /api/v1/logs/ingest` (sans authentification, format JSON libre).

## Tests

```bash
# Exécuter tous les tests (104 tests)
pytest -v

# Avec couverture
pytest --cov=app --cov-report=term-missing

# Tests spécifiques
pytest app/tests/test_services/test_normalization.py -v
pytest app/tests/test_core_security.py -v
pytest app/tests/test_schemas.py -v
pytest app/tests/test_utils_tags.py -v
```

### Couverture des tests

| Module                                       | Tests         | Couverture                                        |
| -------------------------------------------- | ------------- | ------------------------------------------------- |
| Normalisation (auto_tag, extract, normalize) | 44            | ✅ Toutes les règles, formats agent, cas limites |
| Sécurité (hash, JWT, MFA)                  | 18            | ✅ Hash, tokens, TOTP                             |
| Schémas (validation Pydantic)               | 17            | ✅ UserCreate, LogCreate, search                  |
| Utilitaires (Role, Perimeter)                | 17            | ✅ 5 rôles, 4 périmètres, permissions          |
| **Total**                              | **104** | ✅                                                |

## Déploiement

### Docker Compose

```bash
docker-compose up -d
```

### Production

- Utiliser les `Dockerfile.api` et `Dockerfile.worker`
- Orchestration via Kubernetes ou Docker Swarm
- Reverse proxy Nginx avec TLS

## Contribution

1. Créer une branche (`git checkout -b feature/ma-fonctionnalite`)
2. Coder en respectant la structure et les patterns existants
3. Exécuter les tests (`pytest`)
4. Formatter le code (`black . && isort .`)
5. Ouvrir une Pull Request

## Licence

Projet académique — **UCAC ICAM - X3 PROJET INTÉGRATEUR**.

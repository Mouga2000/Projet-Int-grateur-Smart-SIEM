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
                    │   Nginx     │
                    │  (Reverse   │
                    │   Proxy)    │
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
│  PostgreSQL   │  │ Elasticsearch │  │     Redis     │
│ (Métadonnées, │  │  (Logs,       │  │  (Cache,      │
│  Alertes,     │  │   Indexation) │  │   Queue)      │
│  Utilisateurs)│  │               │  │               │
└───────────────┘  └───────────────┘  └───────┬───────┘
                                              │
                                      ┌───────▼───────┐
                                      │  Celery       │
                                      │  (Workers)    │
                                      └───────────────┘
```

## Stack technique

| Composant        | Technologie                          | Rôle                                      |
|------------------|--------------------------------------|-------------------------------------------|
| API              | FastAPI (Python 3.12+)               | Serveur HTTP REST (Uvicorn)               |
| Base de données  | PostgreSQL + SQLAlchemy async        | Stockage des métadonnées, utilisateurs, alertes, règles |
| Recherche & logs | Elasticsearch                        | Indexation et recherche plein texte des logs |
| Cache & queue    | Redis + Celery                       | Cache, files d'attente, tâches asynchrones |
| Authentification | JWT + MFA (TOTP)                     | Sessions sécurisées et multi-facteurs      |
| Logs applicatifs | Loguru                               | Logging structuré avec rotation            |
| Migrations BDD   | Alembic                              | Gestion des évolutions du schéma PostgreSQL |

## Structure détaillée du projet

```
SIEM/
│
├── .env                         # Variables d'environnement (à personnaliser)
├── .env.example                 # Exemple de configuration (à copier)
├── .gitignore                   # Fichiers/dossiers exclus de Git
├── requirements.txt             # Dépendances Python du projet
├── docker-compose.yml           # Orchestration complète (API + DB + ES + Redis + Celery + Nginx)
├── Dockerfile.api               # Construction de l'image Docker de l'API FastAPI
├── Dockerfile.worker            # Construction de l'image Docker du worker Celery
├── README.md                    # Cette documentation
│
├── app/                         # ———— CODE SOURCE PRINCIPAL ————
│   ├── __init__.py
│   ├── main.py                  # Point d'entrée : création de l'app FastAPI,
│   │                             # inclusion des routers, events startup/shutdown
│   │
│   ├── core/                    # Configuration et connexions aux services
│   │   ├── config.py            # Settings via pydantic-settings (lit .env).
│   │   │                         # Centralise : DATABASE_URL, ELASTICSEARCH_HOSTS,
│   │   │                         # REDIS_HOST, SECRET_KEY, JWT_*, etc.
│   │   ├── database.py          # Moteur SQLAlchemy async + session factory.
│   │   │                         # Fournit la dépendance get_db() pour FastAPI
│   │   ├── elasticsearch.py     # Client AsyncElasticsearch. Init au startup,
│   │   │                         # fermeture au shutdown. get_es_client()
│   │   └── redis.py             # Client Redis async (cache + rate limiting).
│   │                             # get_redis(), close_redis()
│   │
│   ├── api/                     # Couche API FastAPI
│   │   ├── dependencies.py      # Dépendances injectables : get_current_user(),
│   │   │                         # get_current_admin(), pagination, filtres
│   │   ├── middleware.py        # Configuration des middlewares : CORS,
│   │   │                         # TrustedHost, logging des requêtes, rate limiting
│   │   └── v1/                  # Routes API version 1
│   │       ├── router.py        # Regroupe tous les routeurs v1 dans api_router
│   │       ├── health.py        # GET /health — healthcheck (DB, ES, Redis)
│   │       │                     # GET /ready — readiness probe
│   │       │                     # GET /live — liveness probe
│   │       ├── auth.py          # POST /auth/login — authentification JWT
│   │       │                     # POST /auth/refresh — rafraîchir un token
│   │       │                     # POST /auth/logout — révoquer un token
│   │       │                     # POST /auth/mfa/* — config/vérifier TOTP
│   │       │                     # GET /auth/me — profil utilisateur courant
│   │       ├── users.py         # CRUD /users — gestion des utilisateurs
│   │       │                     # (admin : création, liste, suppression)
│   │       ├── logs.py          # POST /logs/ingest — réception des logs
│   │       │                     # GET /logs — liste paginée des métadonnées
│   │       │                     # GET /logs/{id} — détail d'un log
│   │       ├── search.py        # POST /search — recherche avancée Elasticsearch
│   │       │                     # GET /search/saved — recherches sauvegardées
│   │       ├── alerts.py        # CRUD /alerts — alertes de sécurité
│   │       │                     # POST /alerts/{id}/acknowledge — prise en charge
│   │       │                     # POST /alerts/{id}/escalate — escalade
│   │       ├── playbooks.py     # CRUD /playbooks — playbooks SOAR
│   │       │                     # POST /playbooks/{id}/execute — exécution
│   │       └── reports.py       # GET /reports/dashboard — stats tableau de bord
│   │                             # POST /reports/generate — génération rapports
│   │                             # POST /reports/schedule — rapports programmés
│   │
│   ├── models/                  # Modèles SQLAlchemy (tables PostgreSQL)
│   │   ├── base.py              # Base déclarative + mixins :
│   │   │                         # TimestampMixin (created_at, updated_at),
│   │   │                         # SoftDeleteMixin (deleted_at)
│   │   ├── user.py              # User — utilisateurs de la plateforme
│   │   │                         # (email, username, hashed_password, rôle, MFA)
│   │   ├── alert.py             # Alert — alerte générée par corrélation
│   │   │                         # (titre, sévérité, statut, règle associée,
│   │   │                         #  score, assignation, logs ES liés)
│   │   ├── rule.py              # Rule — règle de corrélation/détection
│   │   │                         # (type : single_event, threshold, correlation,
│   │   │                         #  sequence, ueba ; condition JSON, actions)
│   │   ├── playbook.py          # Playbook — automatisation SOAR
│   │   │                         # (steps, trigger, variables, timeout)
│   │   ├── incident.py          # Incident — regroupement d'alertes liées
│   │   │                         # (statut, sévérité, alertes liées, MITRE,
│   │   │                         #  investigator, remediation)
│   │   ├── notification.py      # Notification — notifications utilisateur
│   │   │                         # (canal : in_app, email, slack ; référence)
│   │   ├── audit_log.py         # AuditLog — trace de toutes les actions
│   │   │                         # sensibles (qui a fait quoi, quand, IP)
│   │   └── log.py               # LogMetadata — métadonnées des logs
│   │                             # (référence ES, source, host, type,
│   │                             #  hash déduplication, tags)
│   │
│   ├── schemas/                 # Schémas Pydantic (validation API)
│   │   ├── log_schemas.py       # LogCreate, LogResponse, LogListResponse
│   │   ├── alert_schemas.py     # AlertUpdate, AlertResponse, AlertListResponse
│   │   │                         # PlaybookCreate, PlaybookUpdate, PlaybookResponse
│   │   ├── user_schemas.py      # UserCreate, UserUpdate, UserResponse, UserListResponse
│   │   │                         # TokenResponse, LoginRequest
│   │   ├── search_schemas.py    # SearchRequest, FilterCriteria, DateRange,
│   │   │                         # SearchHit, SearchResponse
│   │   └── report_schemas.py    # ReportRequest, ReportResponse, DashboardStats,
│   │                             # ScheduledReport
│   │
│   ├── services/                # Logique métier (traitements)
│   │   ├── normalization.py     # Normalisation des logs bruts (Syslog RFC 3164/5424,
│   │   │                         # CEF, LEEF, Windows Event, JSON) en format commun
│   │   ├── correlation.py       # Moteur de corrélation : évalue chaque log contre
│   │   │                         # les règles actives, détecte patterns (threshold,
│   │   │                         # séquence, multi-sources), génère les alertes
│   │   ├── ueba.py              # Analyse comportementale (ML) : profilage utilisateur/
│   │   │                         # hôte, détection d'anomalies (login, mouvement
│   │   │                         # latéral, exfiltration), scoring
│   │   ├── soar.py              # Orchestration SOAR : exécution des playbooks,
│   │   │                         # actions (enrichissement IP/domaine, blocage,
│   │   │                         # notification Slack/email, ticketing)
│   │   ├── alerts.py            # Gestion des alertes : CRUD + logique métier
│   │   │                         # (acquittement, escalade, résolution, stats)
│   │   ├── search.py            # Recherche Elasticsearch : DSL, agrégations,
│   │   │                         # auto-complétion, sauvegarde de recherches
│   │   ├── reports.py           # Rapports : statistiques dashboard, génération
│   │   │                         # PDF/CSV, programmation de rapports récurrents
│   │   └── auth.py              # Authentification : vérification credentials,
│   │                             # création/validation JWT, MFA/TOTP, refresh tokens
│   │
│   ├── repositories/            # Pattern Repository (accès aux données)
│   │   ├── base.py              # Classe générique CRUD (get, get_multi, create,
│   │   │                         # update, delete, count, exists)
│   │   ├── log_repo.py          # LogMetadata : recherche par ES ID, stats par source
│   │   ├── alert_repo.py        # Alert : filtres par statut/sévérité/règle, stats
│   │   ├── user_repo.py         # User : recherche par email/username, last_login
│   │   ├── audit_repo.py        # AuditLog : log_action, filtres par user/action/date
│   │   ├── rule_repo.py         # Rule : règles actives, filtres par type/MITRE
│   │   ├── playbook_repo.py     # Playbook : playbooks actifs, par trigger
│   │   └── incident_repo.py     # Incident : incidents actifs, par statut/sévérité
│   │
│   ├── tasks/                   # Tâches asynchrones Celery
│   │   ├── celery.py            # Configuration de l'application Celery (broker Redis,
│   │   │                         # backend, beat_schedule, timeouts)
│   │   ├── notification_tasks.py# Envoi emails SMTP, notifications Slack, in-app,
│   │   │                         # nettoyage des vieux logs
│   │   ├── soar_tasks.py        # Exécution de playbooks, enrichissement IP/domaine,
│   │   │                         # blocage asynchrone
│   │   ├── ueba_tasks.py        # Entraînement du modèle ML, scoring des activités,
│   │   │                         # détection mouvement latéral/exfiltration
│   │   └── report_tasks.py      # Génération de rapports PDF/CSV, rapport quotidien
│   │
│   ├── utils/                   # Fonctions utilitaires
│   │   ├── logging.py           # Configuration Loguru (console + fichier avec rotation)
│   │   ├── security.py          # Hash bcrypt, création/décodage JWT, génération
│   │   │                         # et vérification TOTP (MFA)
│   │   ├── validators.py        # Validation IP, domaine, hash, port, sanitization
│   │   ├── mitre.py             # Base de données MITRE ATT&CK (techniques, tactiques,
│   │   │                         # mapping ID -> nom/catégorie)
│   │   └── tags.py              # Constances : niveaux de criticité, types de logs,
│   │                             # mapping source -> protocole/port
│   │
│   └── tests/                   # Tests unitaires et d'intégration
│       ├── conftest.py          # Fixtures pytest (client HTTP, DB de test,
│       │                         # utilisateur de test, headers auth)
│       ├── test_api/            # Tests des endpoints API
│       │   ├── test_auth.py     # Connexion, refresh, logout, accès sans token
│       │   ├── test_logs.py     # Ingestion, listing, pagination, 404
│       │   ├── test_alerts.py   # CRUD alertes, filtres, acquittement, escalade
│       │   └── test_search.py   # Recherche, filtres, pagination, sauvegarde
│       ├── test_services/       # Tests des services métier
│       │   ├── test_normalization.py  # Parsing Syslog, CEF, JSON, enrichment
│       │   ├── test_correlation.py    # Règles single_event, threshold, séquence
│       │   └── test_ueba.py           # Profilage, anomalies, mouvement latéral
│       └── test_repositories/   # Tests d'accès aux données
│           ├── test_log_repo.py       # CRUD métadonnées, purge
│           └── test_user_repo.py      # CRUD utilisateurs, recherche, soft-delete
│
├── migrations/                  # Migrations Alembic PostgreSQL
│   ├── env.py                   # Configuration Alembic (importe tous les modèles,
│   │                             # lit DATABASE_SYNC_URL depuis config)
│   └── versions/                # Scripts de migration générés automatiquement
│       └── .keep
│
└── scripts/                     # Scripts utilitaires en ligne de commande
    ├── generate_dataset_ctu.py  # Génération d'un dataset de test : trafic normal +
    │                             # scénarios malveillants (bruteforce, scan, malware,
    │                             # exfiltration, insider threat)
    ├── populate_test_data.py    # Peuplement de la base avec données de démo :
    │                             # utilisateurs, règles, playbooks, logs exemples
    └── seed_rules.py            # Initialisation des règles de corrélation par défaut
                                # (bruteforce SSH, port scan, commandes suspectes,
                                #  horaires inhabituels, téléchargements massifs)
```

## Installation

### Prérequis

- **Python 3.12+**
- **PostgreSQL 16+**
- **Elasticsearch 8.x**
- **Redis 7+**
- Accès à un terminal (PowerShell, bash, etc.)

### Étapes

```bash
# 1. Cloner le dépôt
git clone <url-du-repo>
cd SIEM

# 2. Créer et activer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\Activate    # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env .env.local          # Adapter les valeurs

# 5. Initialiser la base de données
alembic upgrade head

# 6. Démarrer l'API
uvicorn app.main:app --reload
```

### Avec Docker

```bash
docker-compose up -d
```

## Démarrage rapide

```bash
# Démarrer l'API
uvicorn app.main:app --reload

# Démarrer le worker Celery
celery -A app.tasks.celery worker --loglevel=info

# Lancer les tests
pytest -v
```

## API Endpoints

| Méthode | Endpoint                | Description              | Auth     |
|---------|------------------------|--------------------------|----------|
| POST    | `/api/v1/auth/login`   | Authentification         | ✗        |
| GET     | `/api/v1/auth/me`      | Profil utilisateur       | ✓        |
| GET     | `/api/v1/health/`      | Health check             | ✗        |
| GET     | `/api/v1/users/`       | Liste des utilisateurs   | Admin    |
| POST    | `/api/v1/logs/ingest`  | Ingestion de logs        | ✓        |
| GET     | `/api/v1/logs/`        | Liste des logs           | ✓        |
| POST    | `/api/v1/search/`      | Recherche plein texte    | ✓        |
| GET     | `/api/v1/alerts/`      | Liste des alertes        | ✓        |
| PATCH   | `/api/v1/alerts/{id}`  | Mise à jour d'une alerte | ✓        |
| POST    | `/api/v1/playbooks/`   | Créer un playbook        | Admin    |
| GET     | `/api/v1/reports/dashboard` | Statistiques tableau de bord | ✓ |

> La liste complète est disponible via Swagger à `http://localhost:8000/docs`

## Tests

```bash
# Exécuter tous les tests
pytest -v

# Avec couverture
pytest --cov=app --cov-report=term-missing

# Tests spécifiques
pytest app/tests/test_api/test_auth.py -v
```

## Déploiement

### Docker Compose (développement)

```bash
docker-compose up -d
```

### Production

- Utiliser les `Dockerfile.api` et `Dockerfile.worker` pour construire les images
- Orchestration via Kubernetes ou Docker Swarm
- Reverse proxy Nginx avec TLS
- Base de données gérée (RDS, Cloud SQL) ou auto-hébergée

## Contribution

1. Créer une branche (`git checkout -b feature/ma-fonctionnalite`)
2. Coder en suivant la structure existante (commentaires-guides dans chaque fichier)
3. Exécuter les tests (`pytest`)
4. Formatter le code (`black . && isort .`)
5. Ouvrir une Pull Request

## Licence

Projet académique — **UCAC ICAM - X3 PROJET INTÉGRATEUR**.

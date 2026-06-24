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
│ Elasticsearch │  │     Redis     │  │    Celery     │
│  (Données     │  │  (Cache,      │  │  (Workers     │
│  centralisées)│  │   Queue)      │  │   asynchrones)│
└───────────────┘  └───────────────┘  └───────────────┘
```

## Stack technique

| Composant        | Technologie                          | Rôle                                      |
|------------------|--------------------------------------|-------------------------------------------|
| API              | FastAPI (Python 3.12+)               | Serveur HTTP REST (Uvicorn)               |
| Base de données  | Elasticsearch (stockage unique)      | Utilisateurs, audit, logs, alertes, règles…|
| Cache & queue    | Redis + Celery                       | Cache, files d'attente, tâches asynchrones |
| Authentification | JWT + MFA (TOTP)                     | Sessions sécurisées et multi-facteurs      |
| Logs applicatifs | Loguru                               | Logging structuré avec rotation            |

> Toutes les données sont stockées dans **Elasticsearch** — pas de PostgreSQL. Le projet utilise Elasticsearch comme base de données centralisée (documents JSON, index par type de données).

## Structure détaillée du projet

**Légende :** ✅ = implémenté | ⏳ = en commentaire (à coder)

```
SIEM/
│
├── .env                         # Variables d'environnement (ES + JWT)
├── .gitignore                   # Fichiers/dossiers exclus de Git
├── requirements.txt             # Dépendances Python du projet
├── docker-compose.yml           # Orchestration Docker
├── Dockerfile.api               # Image Docker de l'API FastAPI
├── Dockerfile.worker            # Image Docker du worker Celery
├── README.md                    # Cette documentation
│
├── app/                         # ———— CODE SOURCE PRINCIPAL ————
│   ├── main.py                  # ✅ Point d'entrée FastAPI (auth + users routers)
│   │
│   ├── core/                    # Configuration et connexions aux services
│   │   ├── config.py            # ✅ Settings JWT + Elasticsearch (pydantic-settings)
│   │   ├── security.py          # ✅ Hash bcrypt, JWT, MFA/TOTP avec QR code
│   │   ├── elasticsearch.py     # ✅ Client ES singleton AsyncElasticsearch
│   │   ├── database.py          # ⏳ Documentation uniquement (ES-only, voir elasticsearch.py)
│   │   └── redis.py             # ⏳ Client Redis async (cache + rate limiting)
│   │
│   ├── api/                     # Couche API FastAPI
│   │   ├── dependencies.py      # ✅ get_current_user, require_role (utilise enum Role)
│   │   ├── middleware.py        # ⏳ CORS, TrustedHost, logging, rate limiting
│   │   └── v1/                  # Routes API version 1
│   │       ├── auth.py          # ✅ Login, logout, MFA (setup, verify, disable, status)
│   │       ├── users.py         # ✅ CRUD users + /setup + /{username}/role + /{username}/perimeter
│   │       ├── router.py        # ✅ Routeur central (auth, users, logs actifs)
│   │       ├── logs.py          # ✅ POST /logs/ingest, GET /logs, POST /logs/search, GET /logs/{id}
│   │       ├── search.py        # ⏳ POST /search, GET /search/saved
│   │       ├── alerts.py        # ⏳ CRUD /alerts, acknowledge, escalate
│   │       ├── playbooks.py     # ⏳ CRUD /playbooks, POST /{id}/execute
│   │       ├── reports.py       # ⏳ GET /reports/dashboard, POST /reports/generate, schedule
│   │       └── router.py        # ⏳ Regroupement des routeurs
│   │
│   ├── models/                  # Modèles Pydantic → documents Elasticsearch
│   │   ├── user.py              # ✅ Modèle User (username, email, role, MFA, perimètre)
│   │   ├── log.py               # ⏳ Log de sécurité normalisé
│   │   ├── alert.py             # ⏳ Alerte de sécurité
│   │   ├── rule.py              # ⏳ Règle de corrélation
│   │   ├── playbook.py          # ⏳ Playbook SOAR
│   │   ├── incident.py          # ⏳ Incident de sécurité
│   │   ├── notification.py      # ⏳ Notification utilisateur
│   │   └── audit_log.py         # ⏳ Trace d'audit
│   │
│   ├── schemas/                 # Schémas Pydantic (validation API)
│   │   ├── user_schemas.py      # ✅ UserCreate (avec enum Role), UserLogin, Token, UserResponse…
│   │   ├── log_schemas.py       # ⏳ LogCreate, LogResponse, LogListResponse
│   │   ├── alert_schemas.py     # ⏳ AlertUpdate, AlertResponse, PlaybookCreate…
│   │   ├── search_schemas.py    # ⏳ SearchRequest, SearchHit, SearchResponse
│   │   └── report_schemas.py    # ⏳ ReportRequest, DashboardStats, ScheduledReport
│   │
│   ├── services/                # Logique métier
│   │   ├── auth.py              # ✅ AuthService (authenticate avec MFA, logout, audit trail)
│   │   ├── audit_service.py     # ✅ AuditService (login/logout/MFA/gestion logs)
│   │   ├── normalization.py     # ✅ Pipeline : auto_tag, extract_structured, normalize
│   │   ├── correlation.py       # ⏳ Moteur de corrélation (threshold, séquence)
│   │   ├── ueba.py              # ⏳ Analyse comportementale (ML)
│   │   ├── soar.py              # ⏳ Orchestration SOAR (playbooks)
│   │   ├── alerts.py            # ⏳ Gestion des alertes
│   │   ├── search.py            # ⏳ Recherche Elasticsearch DSL
│   │   └── reports.py           # ⏳ Rapports PDF/CSV
│   │
│   ├── repositories/            # Pattern Repository (accès Elasticsearch)
│   │   ├── user_repo.py         # ✅ CRUD utilisateurs (create, get, update, list, delete)
│   │   ├── audit_repo.py        # ✅ Audit logs (login, logout, MFA, user management)
│   │   ├── log_repo.py          # ✅ Logs de sécurité (ingest, search, get_by_id, count, delete)
│   │   ├── alert_repo.py        # ⏳ Alertes
│   │   ├── rule_repo.py         # ⏳ Règles
│   │   ├── playbook_repo.py     # ⏳ Playbooks
│   │   └── incident_repo.py     # ⏳ Incidents
│   │
│   ├── tasks/                   # Tâches asynchrones Celery
│   │   ├── celery.py            # ⏳ Configuration Celery
│   │   ├── notification_tasks.py# ⏳ Envoi emails, Slack, nettoyage logs
│   │   ├── soar_tasks.py        # ⏳ Exécution playbooks, enrichissement
│   │   ├── ueba_tasks.py        # ⏳ Entraînement ML, scoring anomalies
│   │   └── report_tasks.py      # ⏳ Génération de rapports
│   │
│   ├── utils/                   # Fonctions utilitaires
│   │   ├── tags.py              # ✅ Enum Role (5 rôles) + Enum Perimeter (4 niveaux) + ROLE_PERMISSIONS_MAP
│   │   ├── logging.py           # ⏳ Configuration Loguru
│   │   ├── validators.py        # ⏳ Validation IP, domaine, hash…
│   │   └── mitre.py             # ⏳ Base MITRE ATT&CK
│   │
│   └── tests/                   # Tests
│       ├── conftest.py          # ⏳ Fixtures pytest (ES-based)
│       ├── test_api/            # ⏳ Tests auth, logs, alerts, search
│       ├── test_services/       # ⏳ Tests services métier
│       └── test_repositories/   # ⏳ Tests repositories
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

| Endpoint | Méthode | Description | Auth |
|---|---|---|---|
| `POST /api/v1/auth/login` | POST | Connexion (username/password + MFA optionnelle) | Public |
| `POST /api/v1/auth/logout` | POST | Déconnexion | Token |
| `GET  /api/v1/auth/mfa/status` | GET | Voir si la MFA est activée | Token |
| `POST /api/v1/auth/mfa/setup` | POST | Générer le secret TOTP + QR code | Token |
| `POST /api/v1/auth/mfa/verify` | POST | Activer la MFA après vérification du code | Token |
| `POST /api/v1/auth/mfa/disable` | POST | Désactiver la MFA (avec confirmation mot de passe) | Token |
| `GET  /api/v1/users/` | GET | Liste des utilisateurs | Admin |
| `POST /api/v1/users/` | POST | Créer un utilisateur | Admin |
| `PUT  /api/v1/users/{username}/role` | PUT | Modifier le rôle d'un utilisateur | Admin |
| `PUT  /api/v1/users/{username}/perimeter` | PUT | Modifier le périmètre d'un utilisateur | Admin |
| `POST /api/v1/users/setup` | POST | **Bootstrap** : créer le premier admin (sans auth) | Public |
| `GET  /api/v1/users/me` | GET | Profil de l'utilisateur connecté | Token |

#### 📥 Logs

| Endpoint | Méthode | Description | Auth |
|---|---|---|---|
| `POST /api/v1/logs/ingest` | POST | Ingérer un log (normalisation + tagging + indexation ES) | Token |
| `GET  /api/v1/logs/` | GET | Liste paginée des logs | Token |
| `POST /api/v1/logs/search` | POST | Recherche avancée (filtres, dates, sources) | Token |
| `GET  /api/v1/logs/{id}` | GET | Détail d'un log par ID ES | Token |
| `DELETE /api/v1/logs/{id}` | DELETE | Supprimer un log | Token |

**Fonctionnalités :**
- Hash bcrypt des mots de passe
- Tokens JWT (access + refresh)
- MFA TOTP avec QR code (optionnelle, activable par utilisateur)
- 5 rôles : `lecteur`, `analyste`, `auditeur`, `rssi`, `administrateur` (enum `Role`)
- 4 périmètres fonctionnels : `equipe`, `service`, `filiale`, `environnement` (enum `Perimeter`)
- Système de permissions granulaires (RBAC via `ROLE_PERMISSIONS_MAP`)
- Audit trail des connexions dans Elasticsearch
- Normalisation automatique des logs (tagging criticité/type + enrichissement)
- Stockage dans Elasticsearch (index `users`, `audit-YYYY-MM-DD`, `logs-YYYY-MM-DD`)

### ⏳ En cours / À faire

| Module | Priorité | Description |
|---|---|---|
| **Alertes** | Haute | CRUD + workflow (acquittement, escalade) |
| **Règles de corrélation** | Haute | Moteur de détection |
| **Règles de corrélation** | Haute | Moteur de détection |
| **Playbooks SOAR** | Moyenne | Automatisation des réponses |
| **Rapports** | Moyenne | Dashboard stats + génération PDF/CSV |
| **UEBA** | Basse | Analyse comportementale (ML) |
| **Tasks Celery** | Basse | Tâches asynchrones |
| **Tests** | Haute | Couverture pytest |

## Installation

### Prérequis

- **Python 3.12+**
- **Elasticsearch 8.x** (base de données unique du projet) — [téléchargement](https://www.elastic.co/downloads/elasticsearch)
- **Redis 7+** (pour Celery, optionnel au démarrage)

### Étapes

```bash
# 1. Cloner le dépôt
git clone <url-du-repo>
cd SIEM

# 2. Créer et activer l'environnement virtuel
python -m venv venv
.\venv\Scripts\Activate    # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
#    Copier .env et renseigner SECRET_KEY, ELASTICSEARCH_HOST, etc.

# 5. Lancer Elasticsearch (obligatoire)
#    Docker : docker run -d --name es -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" docker.elastic.co/elasticsearch/elasticsearch:8.11.0

# 6. Lancer l'API
uvicorn app.main:app --reload

# 7. Créer le premier administrateur (bootstrap)
curl -X POST http://localhost:8000/api/v1/users/setup \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "email": "admin@siem.local", "password": "admin123!", "role": "lecteur", "perimeter": []}'
```

> **Note :** L'endpoint `/users/setup` crée le premier admin (le rôle est forcé à `administrateur`). Il n'est accessible que s'il n'y a encore aucun utilisateur.

### Avec Docker

```bash
docker-compose up -d
```

### Index Elasticsearch utilisés

| Index | Contenu |
|---|---|
| `users` | Profils utilisateurs, mots de passe hashés, rôles |
| `audit-YYYY-MM-DD` | Journal des actions (login, logout, MFA, gestion) |
| `logs-YYYY-MM-DD` | Logs de sécurité normalisés (timestamp, source_ip, host, log_type, severity, raw_message) |
| `alerts` | Alertes générées (à venir) |
| `rules` | Règles de corrélation (à venir) |
| `playbooks` | Playbooks SOAR (à venir) |
| `incidents` | Incidents de sécurité (à venir) |
| `notifications` | Notifications utilisateur (à venir) |

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

## Contribution

1. Créer une branche (`git checkout -b feature/ma-fonctionnalite`)
2. Coder en suivant la structure existante (commentaires-guides dans chaque fichier)
3. Exécuter les tests (`pytest`)
4. Formatter le code (`black . && isort .`)
5. Ouvrir une Pull Request

## Licence

Projet académique — **UCAC ICAM - X3 PROJET INTÉGRATEUR**.

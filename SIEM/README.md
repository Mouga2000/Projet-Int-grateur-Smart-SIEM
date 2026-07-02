
# Smart SIEM — Backend

Plateforme SIEM (Security Information and Event Management) intelligente avec ingestion universelle de logs, normalisation automatique, analyses comportementales (UEBA/ML), investigations croisées, archivage conforme et orchestration SOAR.

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
│  Règles,       │  │   Profiles    │  │   Celery)     │
│  Audits,       │  │   CLUE-LDS)   │  │               │
│  Investigations│  │               │  │               │
│  Archives,     │  │               │  │               │
│  Profils UEBA) │  │               │  │               │
└───────────────┘  └───────────────┘  └───────┬───────┘
                                              │
                                      ┌───────▼───────┐
                                      │    Celery     │
                                      │  (Beat +      │
                                      │   Entraînement│
                                      │   UEBA, Purge)│
                                      └───────────────┘
```

**Architecture duale :**

- **PostgreSQL** — données structurées : utilisateurs, règles, audits, investigations, archives, profils UEBA
- **Elasticsearch** — données volumineuses : logs de sécurité (index `logs-clue`) + datasets BOTSv3/CLUE

---

## Stack technique

| Composant           | Technologie                          | Rôle                                         |
| ------------------- | ------------------------------------ | --------------------------------------------- |
| API                 | FastAPI 0.138 + Python 3.14          | Serveur HTTP REST (Uvicorn)                   |
| Base de données    | PostgreSQL 17 + SQLAlchemy 2.0 async | Utilisateurs, règles, audits, investigations |
| Moteur de recherche | Elasticsearch 8.11                   | Logs, recherche plein texte, agrégations     |
| Cache & queue       | Redis + Celery                       | Broker tâches, purge, compteurs corrélation |
| ML/UEBA             | scikit-learn (Isolation Forest)      | Analyse comportementale, scoring risque       |
| Authentification    | JWT (HS256) + MFA (TOTP/pyotp)       | Sessions sécurisées et multi-facteurs       |
| Chiffrement         | cryptography (RSA 2048)              | Signatures archives, non-répudiation         |
| Migrations          | Alembic                              | Évolution du schéma PostgreSQL              |
| Tests               | pytest + pytest-asyncio + httpx      | 387 tests unitaires et API                    |
| Docker              | Docker Compose                       | Elasticsearch + Kibana + API conteneurisés   |

---

## Structure détaillée du projet

```
SIEM/
│
├── .env                         # Variables d'environnement
├── .gitignore
├── .dockerignore
├── requirements.txt             # Dépendances Python
├── docker-compose.yml           # Elasticsearch + Kibana + API
├── Dockerfile                   # Image Docker de l'API
├── alembic.ini                  # Configuration migrations
├── README.md
│
├── certs/                       # Clé RSA auto-générée pour les archives
│   └── archive_key.pem
│
├── data/archives/               # Fichiers JSON compressés (archives certifiées)
│
├── models/ueba/                 # Modèle ML entraîné (Isolation Forest)
│   └── isolation_forest.joblib  # Entraîné sur 50M événements CLUE-LDS
│
├── app/
│   ├── main.py                  # Point d'entrée (lifespan, init_db, routers)
│   │
│   ├── core/                    # Configuration et connexions
│   │   ├── config.py            # Settings (JWT, PostgreSQL, ES, UEBA, rétention)
│   │   ├── security.py          # Hash bcrypt, JWT, MFA/TOTP avec QR code
│   │   ├── elasticsearch.py     # Client ES singleton AsyncElasticsearch
│   │   ├── database.py          # SQLAlchemy async + init_db() (création auto des tables)
│   │   └── redis.py             # Client Redis async (cache, compteurs seuil)
│   │
│   ├── api/
│   │   ├── dependencies.py      # get_current_user, require_role, require_permissions
│   │   └── v1/
│   │       ├── router.py        # Routeur central
│   │       ├── auth.py          # Login, logout, MFA (setup, verify, disable, status)
│   │       ├── users.py         # CRUD users + /setup + /{username}/role/perimeter
│   │       ├── logs.py          # Ingest, list, search, timeline, get, delete
│   │       ├── alerts.py        # CRUD alertes + filtres + stats
│   │       ├── rules.py         # CRUD règles de corrélation
│   │       ├── incidents.py     # CRUD incidents + statut + timeline + assignation
│   │       ├── investigations.py# CRUD investigations + logs + verdicts
│   │       ├── notifications.py # Notifications in-app (liste, lecture)
│   │       ├── playbooks.py     # CRUD playbooks SOAR + execution
│   │       ├── mitre.py         # Endpoints MITRE ATT&CK
│   │       ├── admin.py         # Purge logs/audit + rétention
│   │       ├── archive.py       # Archive certifiée (créer, lister, vérifier, exporter)
│   │       ├── audit.py         # Logs d'audit PostgreSQL (GET + export CSV)
│   │       └── ueba.py          # Profils UEBA, scores de risque
│   │
│   ├── models/
│   │   └── sql_models.py        # User, Rule, Playbook, Incident, Alert, ProfilUEBA,
│   │                            # AuditLog, Notification, Archive, Investigation, Agent
│   │
│   ├── schemas/
│   │   ├── user_schemas.py      # UserCreate, UserLogin, UserResponse, UserUpdateRole
│   │   ├── log_schemas.py       # RawLog, LogCreate, LogResponse, LogSearchRequest
│   │   └── alert_schemas.py     # AlertResponse, AlertUpdate
│   │
│   ├── services/
│   │   ├── auth.py              # AuthService (authenticate avec MFA, audit)
│   │   ├── normalization.py     # auto_tag, extract_structured, normalize
│   │   ├── archiver.py          # SHA-256, Merkle tree, chaîne, signature RSA
│   │   ├── correlation.py       # 5 types : single, threshold, sequence, correlation, UEBA
│   │   ├── soar.py              # SOAR (block_ip, disable_user, isolate_host, notifications)
│   │   ├── notification_service.py # Multi-canal (in-app, email, Slack)
│   │   ├── email_templating.py  # Rendu HTML des emails d'alerte
│   │   └── ueba.py              # Isolation Forest, feature extraction, scoring 0-100
│   │
│   ├── repositories/            # Pattern Repository (accès données)
│   │   ├── user_repo.py         # CRUD utilisateurs PostgreSQL
│   │   ├── audit_repo.py        # Audit logs PostgreSQL + purge
│   │   ├── log_repo.py          # CRUD logs ES (ingest, bulk, search, timeline)
│   │   ├── archive_repo.py      # Archives PostgreSQL
│   │   ├── investigation_repo.py# Investigations PostgreSQL
│   │   ├── incident_repo.py     # Incidents PostgreSQL (status, timeline)
│   │   ├── alert_repo.py        # Alertes PostgreSQL
│   │   ├── rule_repo.py         # Règles PostgreSQL
│   │   ├── playbook_repo.py     # Playbooks PostgreSQL
│   │   └── notification_repo.py # Notifications PostgreSQL
│   │
│   ├── tasks/
│   │   ├── archive_tasks.py     # auto_archive_logs (Celery Beat dimanche 3h)
│   │   ├── celery.py            # Config Celery + Beat schedule
│   │   ├── notification_tasks.py # purge_old_logs, send_email, send_slack
│   │   ├── soar_tasks.py        # Tâches SOAR asynchrones
│   │   ├── report_tasks.py      # Génération de rapports
│   │   └── ueba_tasks.py        # train_anomaly_model, score_single_event
│   │
│   ├── utils/
│   │   ├── tags.py              # Role (5 rôles), Perimeter (4 niveaux), permissions
│   │   └── mitre.py             # Base MITRE ATT&CK (36 techniques, 14 tactiques)
│   │
│   └── tests/                   # 387 tests
│       ├── conftest.py          # Fixtures partagées
│       ├── test_core_security.py
│       ├── test_schemas.py
│       ├── test_utils_tags.py
│       ├── test_correlation.py
│       ├── test_services/       # normalization, auth, ueba, soar, archiver,
│       │                        # notification_service, email_templating, audit_service
│       ├── test_repositories/   # user, log, alert, rule, incident, investigation,
│       │                        # notification, playbook, archive, audit
│       └── test_api/            # auth, logs, ueba
│
├── scripts/
│   ├── seed_rules.py            # 7 règles de corrélation MITRE
│   ├── seed_playbooks.py        # 3 playbooks SOAR
│   ├── train_ueba.py            # Entraînement modèle UEBA (fichier ou ES)
│   ├── evaluate_ueba.py         # Évaluation des performances du modèle
│   ├── ingest_clue_lds.py       # Ingestion dataset CLUE-LDS (50M events)
│   ├── simulate_ueba_attack.py  # Simulation attaque pour validation UEBA
│   └── test_smtp.py             # Test d'envoi d'email SMTP
│
└── migrations/
    ├── env.py                   # Configuration Alembic
    └── versions/                # Scripts de migration
```

---

## API REST — Référence complète

### 🔐 Authentification

| Méthode | Endpoint                     | Auth   | Description                                          |
| -------- | ---------------------------- | ------ | ---------------------------------------------------- |
| POST     | `/api/v1/auth/login`       | Public | Authentification (username/password + MFA optionnel) |
| POST     | `/api/v1/auth/logout`      | Token  | Déconnexion (journalisée)                          |
| GET      | `/api/v1/auth/mfa/status`  | Token  | Statut MFA du compte connecté                       |
| POST     | `/api/v1/auth/mfa/setup`   | Token  | Générer un secret TOTP + QR code                   |
| POST     | `/api/v1/auth/mfa/verify`  | Token  | Activer la MFA après vérification du code          |
| POST     | `/api/v1/auth/mfa/disable` | Token  | Désactiver la MFA (mot de passe requis)             |

### 👤 Utilisateurs

| Méthode | Endpoint                               | Auth   | Description                                      |
| -------- | -------------------------------------- | ------ | ------------------------------------------------ |
| GET      | `/api/v1/users/`                     | Admin  | Liste tous les utilisateurs                      |
| POST     | `/api/v1/users/`                     | Admin  | Créer un utilisateur (journalisé)              |
| GET      | `/api/v1/users/me`                   | Token  | Profil de l'utilisateur connecté                |
| POST     | `/api/v1/users/setup`                | Public | Créer le premier administrateur (bootstrap)     |
| PUT      | `/api/v1/users/{username}/role`      | Admin  | Modifier le rôle d'un utilisateur (journalisé) |
| PUT      | `/api/v1/users/{username}/perimeter` | Admin  | Modifier le périmètre (journalisé)            |

### 📥 Logs

| Méthode | Endpoint                  | Auth   | Description                                 |
| -------- | ------------------------- | ------ | ------------------------------------------- |
| POST     | `/api/v1/logs/ingest`   | Public | Ingérer un log (normalisation automatique) |
| GET      | `/api/v1/logs/`         | Token  | Lister les logs (paginé)                   |
| POST     | `/api/v1/logs/search`   | Token  | Recherche multi-critères (10 filtres)      |
| GET      | `/api/v1/logs/timeline` | Token  | Histogramme temporel (10s à 1M)            |
| GET      | `/api/v1/logs/{id}`     | Token  | Détail d'un log                            |
| DELETE   | `/api/v1/logs/{id}`     | Token  | Supprimer un log                            |

### 🧠 UEBA — Analyse Comportementale

| Méthode | Endpoint                             | Auth      | Description                   |
| -------- | ------------------------------------ | --------- | ----------------------------- |
| GET      | `/api/v1/ueba/profile/{entity_id}` | Token     | Profil UEBA + score de risque |
| GET      | `/api/v1/ueba/scores`              | Analyste+ | Top scores de risque          |

### 🔍 Investigations

| Méthode | Endpoint                               | Auth     | Description                                |
| -------- | -------------------------------------- | -------- | ------------------------------------------ |
| POST     | `/api/v1/investigations/`            | Analyste | Créer une investigation                   |
| GET      | `/api/v1/investigations/`            | Token    | Lister les investigations                  |
| GET      | `/api/v1/investigations/{id}`        | Token    | Détail d'une investigation                |
| POST     | `/api/v1/investigations/{id}/logs`   | Analyste | Marquer un log suspect (verdict + note)    |
| PATCH    | `/api/v1/investigations/{id}/status` | Analyste | Changer le statut                          |
| PATCH    | `/api/v1/investigations/{id}`        | Analyste | Modifier (titre, description, assignation) |

### 🚨 Alertes

| Méthode | Endpoint                 | Auth     | Description                                     |
| -------- | ------------------------ | -------- | ----------------------------------------------- |
| GET      | `/api/v1/alerts/`      | Token    | Lister les alertes (filtres sévérité/statut) |
| GET      | `/api/v1/alerts/stats` | Token    | Statistiques par sévérité et statut          |
| GET      | `/api/v1/alerts/{id}`  | Token    | Détail d'une alerte                            |
| PATCH    | `/api/v1/alerts/{id}`  | Analyste | Mettre à jour le statut                        |

### 📋 Incidents

| Méthode | Endpoint                          | Auth     | Description                                       |
| -------- | --------------------------------- | -------- | ------------------------------------------------- |
| GET      | `/api/v1/incidents/`            | Token    | Lister les incidents (filtre statut + pagination) |
| POST     | `/api/v1/incidents/`            | Analyste | Créer un incident (avec timeline)                |
| GET      | `/api/v1/incidents/{id}`        | Token    | Détail + timeline complète                      |
| PATCH    | `/api/v1/incidents/{id}/status` | Analyste | Changer le statut (journalisé)                   |
| POST     | `/api/v1/incidents/{id}/alerts` | Analyste | Ajouter une alerte                                |
| POST     | `/api/v1/incidents/{id}/assign` | Analyste | Assigner à un analyste                           |

### ⚙️ Règles de corrélation

| Méthode | Endpoint               | Auth  | Description             |
| -------- | ---------------------- | ----- | ----------------------- |
| GET      | `/api/v1/rules/`     | Token | Lister les règles      |
| POST     | `/api/v1/rules/`     | Admin | Créer une règle       |
| GET      | `/api/v1/rules/{id}` | Token | Détail d'une règle    |
| PUT      | `/api/v1/rules/{id}` | Admin | Modifier une règle     |
| DELETE   | `/api/v1/rules/{id}` | Admin | Supprimer (soft-delete) |

Types : `single_event`, `threshold` (Redis), `sequence` (Redis), `correlation` (ES), `ueba` (score ML)

### 🤖 Playbooks SOAR

| Méthode | Endpoint                           | Auth     | Description             |
| -------- | ---------------------------------- | -------- | ----------------------- |
| GET      | `/api/v1/playbooks/`             | Token    | Lister les playbooks    |
| POST     | `/api/v1/playbooks/`             | Admin    | Créer un playbook      |
| GET      | `/api/v1/playbooks/{id}`         | Token    | Détail d'un playbook   |
| PUT      | `/api/v1/playbooks/{id}`         | Admin    | Modifier un playbook    |
| DELETE   | `/api/v1/playbooks/{id}`         | Admin    | Supprimer (soft-delete) |
| POST     | `/api/v1/playbooks/{id}/execute` | Analyste | Exécuter un playbook   |

Actions : `block_ip`, `disable_user`, `isolate_host`, `notify_slack`, `notify_email`, `create_ticket`

### 🔔 Notifications

| Méthode | Endpoint                               | Auth  | Description                      |
| -------- | -------------------------------------- | ----- | -------------------------------- |
| GET      | `/api/v1/notifications/`             | Token | Lister mes notifications         |
| GET      | `/api/v1/notifications/unread-count` | Token | Nombre de notifications non lues |
| PATCH    | `/api/v1/notifications/{id}/read`    | Token | Marquer comme lue                |
| POST     | `/api/v1/notifications/read-all`     | Token | Tout marquer comme lu            |

### 📋 Audit

| Méthode | Endpoint                      | Auth     | Description                      |
| ------- | ----------------------------- | -------- | -------------------------------- |
| GET     | `/api/v1/audit/logs`        | Auditeur | Lister les logs d'audit         |
| GET     | `/api/v1/audit/logs/export` | Auditeur | Exporter les logs d'audit (CSV) |

### 🗄️ Archivage (Admin)

| Méthode | Endpoint                              | Auth              | Description                           |
| ------- | ------------------------------------- | ----------------- | ------------------------------------- |
| POST    | `/api/v1/admin/archive/create`      | Admin/Auditeur    | Créer une archive certifiée         |
| GET     | `/api/v1/admin/archive/list`        | Admin/Auditeur    | Lister les archives                   |
| GET     | `/api/v1/admin/archive/chain`       | Admin/Auditeur    | Chaîne de confiance des archives     |
| GET     | `/api/v1/admin/archive/{id}`        | Admin/Auditeur    | Détail d'une archive                 |
| POST    | `/api/v1/admin/archive/verify/{id}` | Admin/Auditeur    | Vérifier l'intégrité d'une archive |
| GET     | `/api/v1/admin/archive/{id}/export` | Admin/Auditeur    | Export pour audit réglementaire      |

### 🛠️ Administration

| Méthode | Endpoint                      | Auth  | Description                    |
| -------- | ----------------------------- | ----- | ------------------------------ |
| POST     | `/api/v1/admin/purge/logs`  | Admin | Purger les logs (rétention)   |
| POST     | `/api/v1/admin/purge/audit` | Admin | Purger les audits (rétention) |
| GET      | `/api/v1/admin/retention`   | Admin | Configuration de rétention    |

### 🎯 MITRE ATT&CK

| Méthode | Endpoint                                    | Auth  | Description             |
| -------- | ------------------------------------------- | ----- | ----------------------- |
| GET      | `/api/v1/mitre/tactics`                   | Token | Liste des 14 tactiques  |
| GET      | `/api/v1/mitre/techniques`                | Token | Liste des 36 techniques |
| GET      | `/api/v1/mitre/techniques/{technique_id}` | Token | Détail d'une technique |

### 🏠 Santé

| Méthode | Endpoint    | Auth   | Description    |
| -------- | ----------- | ------ | -------------- |
| GET      | `/`       | Public | Page d'accueil |
| GET      | `/health` | Public | Health check   |

---

## 3. FONCTIONNALITÉS DU SYSTÈME

### 3.1 Collecte et Normalisation des Logs

**Fichiers :** `app/services/normalization.py`, `app/api/v1/logs.py`, `app/schemas/log_schemas.py`

| Fonctionnalité                 | Implémentation                                                                                                                                                                               |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Récepteur universel**  | Endpoint`POST /api/v1/logs/ingest` — accepte tout format JSON, tolérant aux champs manquants                                                                                              |
| **Normalisation**         | `NormalizationService.normalize()` transforme les logs bruts en JSON structuré avec `timestamp`, `source_ip`, `host`, `log_type`, `severity`, `raw_message`                    |
| **Tagging automatique**   | `NormalizationService.auto_tag()` analyse le message brut via 20 règles regex pour assigner `severity` (info/warning/error/critical) et `log_type` (auth/réseau/système/application) |
| **Enrichissement**        | `NormalizationService.extract_structured()` extrait les IPs, MACs, noms d'utilisateurs et ports depuis le message brut                                                                      |
| **Mapping agent → SIEM** | Compatible avec le format agent (`hostname`, `event_type`, `message`) et le format SIEM (`source_ip`, `host`, `raw_message`)                                                      |

---

### 3.2 Stockage, Indexation et Conservation

**Fichiers :** `app/core/database.py`, `app/core/elasticsearch.py`, `app/core/config.py`, `app/services/archiver.py`, `app/api/v1/archive.py`, `app/repositories/log_repo.py`, `app/tasks/notification_tasks.py`

| Fonctionnalité                                | Implémentation                                                                                                                                               |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Indexation des logs**                  | Elasticsearch — indexation par date`logs-YYYY-MM-DD` avec recherche plein texte, filtres et agrégations                                                   |
| **Indexation des données structurées** | PostgreSQL via SQLAlchemy 2.0 async — utilisateurs, règles, alertes, incidents, profils UEBA                                                                |
| **Rétention configurable**              | `LOG_RETENTION_DAYS` (défaut 90j) et `AUDIT_RETENTION_DAYS` (défaut 365j) dans `.env`                                                                 |
| **Purge automatique**                    | Tâche Celery`purge_old_logs()` exécutée quotidiennement à 3h — supprime les logs ES et audits PG obsolètes                                            |
| **Archivage certifié**                  | `ArchiverService.create_archive()` — compression gzip, SHA-256, Merkle tree, chaîne blockchain-like, signature RSA 2048, export pour audit réglementaire |
| **Vérification d'intégrité**          | `ArchiverService.verify_archive()` — vérifie l'existence du fichier, SHA-256, chaîne de hachage et signature temporelle                                  |
| **Endpoints archivage**                  | Créer, lister la chaîne, vérifier, exporter (réservé aux administrateurs)                                                                                |

---

### 3.3 Corrélation d'Événements

**Fichiers :** `app/services/correlation.py`, `app/models/sql_models.py`, `scripts/seed_rules.py`

**Moteur de règles** — `CorrelationEngine.evaluate_event()` supporte 5 types de règles :

| Type                       | Mécanisme                                | Exemple                                            |
| -------------------------- | ----------------------------------------- | -------------------------------------------------- |
| **`single_event`** | Comparaison directe champ → valeur       | `event_type == "login_failed"`                   |
| **`threshold`**    | Compteur Redis avec TTL configurable      | 5 échecs auth en 60 secondes                      |
| **`sequence`**     | Progression d'étapes dans Redis          | Reconnaissance → Lateral Movement → Exfiltration |
| **`correlation`**  | Requête cross-source dans Elasticsearch  | Firewall + AD sur même IP en 5 min                |
| **`ueba`**         | Vérification du score de risque ≥ seuil | Score ≥ 70 → alerte comportementale              |

**Scénarios MITRE ATT&CK pré-définis** (7 règles dans `seed_rules.py`) :

| Scénario         | MITRE                     | Type                                 |
| ----------------- | ------------------------- | ------------------------------------ |
| Brute Force       | T1110 (credential_access) | `threshold` : 5 échecs en 60s     |
| Port Scan         | T1046 (reconnaissance)    | `threshold` : 10 connexions en 30s |
| Pass-the-Hash     | T1550 (lateral_movement)  | `threshold` : 3 NTLM en 300s       |
| Exfiltration C2   | T1041 (exfiltration)      | `threshold` : 10x volume en 900s   |
| Log Deletion      | T1070 (defense_evasion)   | `single_event`                     |
| Firewall + AD     | T1078 (initial_access)    | `correlation` inter-sources        |
| Chaîne complète | T1046 → T1550 → T1041   | `sequence` 3 étapes               |

**Fenêtres temporelles** configurables par règle via `window_seconds` (threshold) et `window_seconds` (sequence).

---

### 3.4 Alertes et Réponse aux Incidents

**Fichiers :** `app/services/correlation.py`, `app/api/v1/alerts.py`, `app/api/v1/incidents.py`, `app/services/soar.py`, `app/services/notification_service.py`, `app/services/email_templating.py`

#### Système d'alertes

| Niveau   | Code                   | Déclenché par                  |
| -------- | ---------------------- | -------------------------------- |
| INFO     | `severity: info`     | Règles de moindre importance    |
| WARNING  | `severity: medium`   | Comportements suspects           |
| HIGH     | `severity: high`     | Règles UEBA, seuils dépassés  |
| CRITICAL | `severity: critical` | Mouvement latéral, exfiltration |

Les alertes sont créées automatiquement par `CorrelationEngine.create_alert()` avec :

- Référence à la règle, IP source, hôte, description
- Tactique et technique MITRE ATT&CK
- Score de confiance (50-100)

#### Notification multi-canal

| Canal            | Technologie                     | Activation                                        |
| ---------------- | ------------------------------- | ------------------------------------------------- |
| **In-app** | PostgreSQL (`notifications`)  | Toujours actif — notifications stockées en base |
| **Email**  | SMTP (STARTTLS) + template HTML | `SMTP_HOST` dans `.env`                       |
| **Slack**  | Webhook HTTP                    | `SLACK_WEBHOOK_URL` dans `.env`               |

Le template d'email (`app/templates/email/alert_notification.html`) inclut :

- En-tête coloré selon la sévérité (rouge → critical, orange → high, etc.)
- Tableau des détails (règle, IP, hôte, type d'événement)
- Badges MITRE ATT&CK
- Lien vers le dashboard SIEM
- Version texte automatique en fallback

Le rendu est assuré par `email_templating.py` (stdlib `string.Template` — zéro dépendance).

#### SOAR — Playbooks automatisés

Actions disponibles (`app/services/soar.py`) :

| Action            | Commande                                    | Cible              |
| ----------------- | ------------------------------------------- | ------------------ |
| `block_ip`      | Bloque une IP sur le pare-feu               | Agent distant HTTP |
| `disable_user`  | Désactive un compte utilisateur            | Agent distant HTTP |
| `isolate_host`  | Isole une machine du réseau                | Agent distant HTTP |
| `notify_slack`  | Envoie une notification Slack               | Slack Webhook      |
| `notify_email`  | Envoie un email                             | SMTP               |
| `create_ticket` | Crée un ticket d'incident (ID: SIEM-XXXXX) | Interne            |

Les playbooks supportent : 4 triggers (manual, alert_created, scheduled, webhook), retry automatique, timeout configurable.

#### Tableau de suivi des incidents

`POST /api/v1/incidents/` crée un incident avec :

- **Statut** : `ouverte → en_cours → resolue → classee`
- **Timeline** : chaque action est horodatée et signée (création, changement de statut, ajout d'alerte, assignation)
- **Assignation** à un analyste
- **Regroupement d'alertes** : un incident peut contenir plusieurs alertes liées

---

### 3.5 Visualisation et Reporting

**Fichiers :** `app/api/v1/alerts.py`, `app/api/v1/logs.py`, `app/api/v1/incidents.py`, `app/api/v1/ueba.py`

| Fonctionnalité              | Endpoint                                  | Description                         |
| ---------------------------- | ----------------------------------------- | ----------------------------------- |
| **Top alertes**        | `GET /api/v1/alerts/?severity=critical` | Liste des alertes par sévérité   |
| **Statistiques**       | `GET /api/v1/alerts/stats`              | Compteurs par sévérité et statut |
| **Volume de logs**     | `GET /api/v1/logs/timeline?interval=1h` | Histogramme temporel                |
| **Scores UEBA**        | `GET /api/v1/ueba/scores?min_score=50`  | Entités les plus risquées         |
| **Profil UEBA**        | `GET /api/v1/ueba/profile/{entity_id}`  | Baseline + score d'une entité      |
| **Timeline incidents** | `GET /api/v1/incidents/{id}`            | Chronologie complète d'un incident |

**Filtres disponibles** dans `POST /api/v1/logs/search` :
`query` (plein texte), `source_ips`, `destination_ips`, `users`, `hosts`, `log_types`, `severities`, `tags`, `date_from`, `date_to`

La visualisation chronologique utilise l'agrégation `date_histogram` d'Elasticsearch avec intervalles de 10s à 1M.

---

### 3.6 Recherche et Investigation

**Fichiers :** `app/api/v1/investigations.py`, `app/repositories/investigation_repo.py`, `app/api/v1/logs.py`

#### Recherche multi-critères

`POST /api/v1/logs/search` supporte 10 filtres combinables :

- IP source et destination (extraite du message)
- Noms d'utilisateurs (extraits du message)
- Hosts
- Types de log (auth, reseau, systeme, application)
- Niveaux de criticité
- Tags
- Plage horaire avec date_from/date_to
- Pagination

#### Timeline interactive

`GET /api/v1/logs/timeline?interval=1h&severities=critical,error`
Retourne un histogramme des événements groupés par intervalle de temps, utilisable directement par des bibliothèques de graphiques (Chart.js, D3.js).

#### Investigation croisée

| Endpoint                                  | Fonction                            |
| ----------------------------------------- | ----------------------------------- |
| `POST /api/v1/investigations/`          | Créer une enquête                 |
| `POST /api/v1/investigations/{id}/logs` | Marquer un log suspect avec verdict |
| `GET /api/v1/investigations/{id}`       | Voir tous les logs de l'enquête    |

Verdicts disponibles : `suspect`, `benign`, `confirmed`, `false_positive`

Chaque investigation est liée aux tactiques/techniques MITRE ATT&CK.

#### Rétention et historique

Les logs sont conservés dans Elasticsearch jusqu'à la limite configurée (`LOG_RETENTION_DAYS`), puis :

- Purge automatique par Celery (quotidien)
- Archivage certifié avant purge (SHA-256 + chaîne)
- Consultation possible via l'API pendant toute la période de rétention

---

### 3.7 Gestion des Utilisateurs et Sécurité d'Accès

**Fichiers :** `app/core/security.py`, `app/services/auth.py`, `app/api/v1/auth.py`, `app/api/v1/users.py`, `app/utils/tags.py`, `app/api/dependencies.py`, `app/repositories/audit_repo.py`

#### Authentification

- **Locale** (username/password) — hachage bcrypt, JWT (access + refresh tokens)
- **MFA TOTP** — génération de secret, QR code, vérification de code (pyotp + qrcode)
- Durée de session configurable (`ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`)

#### RBAC — 5 rôles avec permissions granulaires

| Rôle                    | Permissions                                                 |
| ------------------------ | ----------------------------------------------------------- |
| **Lecteur**        | `read:logs`, `read:dashboard`, `read:reports`         |
| **Analyste**       | +`write:alerts`, `read/write:incidents`, `read:audit` |
| **Auditeur**       | `read:audit`, `read:reports`, `export:data`           |
| **RSSI**           | `read:dashboard`, `read/write:reports`                  |
| **Administrateur** | `*` (toutes les permissions)                              |

Vérification via `require_role()` et `require_permissions()` dans les dépendances FastAPI.

#### Journalisation des actions

Toutes les actions sensibles sont tracées dans `audit_logs` (PostgreSQL) :

| Action                   | Journalisée dans                                           | Détails enregistrés                    |
| ------------------------ | ----------------------------------------------------------- | ---------------------------------------- |
| Connexion                | `AuditRepository.log_login_attempt()`                     | user, IP, succès/échec                 |
| Déconnexion             | `AuditRepository.log_logout()`                            | user                                     |
| MFA                      | `AuditRepository.log_mfa_verification()`                  | user, succès/échec                     |
| Création utilisateur    | `AuditRepository.log_user_management("create_user")`      | admin, new_user, rôle                   |
| Modification rôle       | `AuditRepository.log_user_management("update_role")`      | admin, cible, ancien/nouveau rôle       |
| Modification périmètre | `AuditRepository.log_user_management("update_perimeter")` | admin, cible, ancien/nouveau périmètre |

#### Ségrégation par périmètre

4 niveaux de périmètre (`app/utils/tags.py`) :

- **Équipe** — groupe fonctionnel
- **Service** — unité organisationnelle
- **Filiale** — entité juridique/géographique
- **Environnement** — contexte technique (prod, recette, dev)

Filtrage automatique dans `GET /api/v1/logs/search` : un analyste avec périmètre "équipe" ne voit que les logs tagués "équipe". L'administrateur voit tout.

---

### 3.8 Analyse Comportementale (UEBA)

**Fichiers :** `app/services/ueba.py`, `app/tasks/ueba_tasks.py`, `app/api/v1/ueba.py`, `scripts/train_ueba.py`, `scripts/evaluate_ueba.py`

#### Modélisation du profil comportemental

Chaque entité (utilisateur, hôte) a un profil stocké dans `profils_ueba` (PostgreSQL) :

```json
{
    "entity_id": "poor-turquoise-starfish-packaging",
    "entity_type": "user",
    "risk_score": 60,
    "baseline": {
        "mean_hour": 4.0,        "std_hour": 0.0,
        "total_events": 16,      "unique_ips": 1,
        "unique_users": 1,       "unique_log_types": 7,
        "error_ratio": 0.0,      "critical_ratio": 0.0,
        "avg_bytes": 0.0
    },
    "last_updated": "2026-06-29T15:37:57"
}
```

**9 dimensions** extraites par `extract_features()` :

- Temporelles : `mean_hour`, `std_hour`
- Volume : `total_events`, `avg_bytes`
- Diversité : `unique_ips`, `unique_users`, `unique_log_types`
- Qualité : `error_ratio`, `critical_ratio`

#### Détection d'anomalies

**Modèle ML :** Isolation Forest (scikit-learn) avec `contamination=0.1`

- Entraîné sur **50 522 929 événements** du dataset CLUE-LDS
- **5 389 profils utilisateurs** dans la base
- Sauvegardé dans `models/ueba/isolation_forest.joblib`

**Business rules** (sur-score) : adjonction de points selon les règles métier :

- `error_ratio > 50%` → +15 points
- `critical_ratio > 10%` → +20 points
- `unique_ips > 20` → +10 points
- `avg_bytes > 100 Ko` → +15 points
- `avg_bytes > 1 Mo` → +25 points

#### Scoring de risque dynamique

- **Score 0-100** calculé à chaque événement via `score_single_event()`
- Mis à jour en temps réel dans `profils_ueba`
- Accessible via `GET /api/v1/ueba/profile/{entity_id}`
- Liste des plus hauts scores : `GET /api/v1/ueba/scores?min_score=70`

#### Corrélation comportements ↔ événements de sécurité

Règle `ueba` dans le moteur de corrélation :

```
Log entrant → check_ueba_rule()
  → get_profile(entity_id) → risk_score ≥ 70 ?
    → Création d'une alerte (haute sévérité)
    → Notification multi-canal (email + in-app)
```

#### Pipeline d'entraînement

```
scripts/train_ueba.py --file docs/clue.json
├── 1. Lecture du fichier (50M lignes, ~15 Go)
├── 2. Groupement par utilisateur (5 389 entités)
├── 3. extract_features() → 9 dimensions
├── 4. IsolationForest.fit() → modèle
├── 5. Sauvegarde → models/ueba/isolation_forest.joblib
└── 6. UPDATE profils_ueba (PostgreSQL)

Ré-entraînement automatique : Celery Beat (lundi 2h)
Évaluation : scripts/evaluate_ueba.py → distribution, stats, test synthétique
```

#### Validation par simulation

`scripts/simulate_ueba_attack.py` injecte des événements d'un utilisateur B sous l'identité d'un utilisateur A pour vérifier que le score UEBA augmente (comportement normal → score 10, comportement anormal → score 75).

---

## Installation

### Prérequis

- **Python 3.12+**
- **PostgreSQL 17+**
- **Elasticsearch 8.x**
- **Redis 7+**

### Installation locale

```bash
# 1. Cloner le dépôt
git clone <url-du-repo>
cd SIEM

# 2. Créer et activer l'environnement virtuel
python -m venv venv
.\venv\Scripts\Activate    # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer .env (SECRET_KEY obligatoire)

# 5. Lancer les services (Docker)
docker compose up -d

# 6. Lancer l'API (tables créées automatiquement)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 7. Créer le premier administrateur
curl -X POST http://localhost:8000/api/v1/users/setup \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "email": "admin@siem.local", "password": "admin123!", "role": "lecteur"}'
```

### Variables d'environnement (`.env`)

| Variable                   | Défaut                               | Description         |
| -------------------------- | ------------------------------------- | ------------------- |
| `SECRET_KEY`             | *(obligatoire)*                     | Clé secrète JWT   |
| `DATABASE_URL`           | `postgresql+asyncpg://…/SmartSiem` | URL PostgreSQL      |
| `ELASTICSEARCH_HOST`     | `localhost`                         | Hôte Elasticsearch |
| `REDIS_HOST`             | `localhost`                         | Hôte Redis         |
| `LOG_RETENTION_DAYS`     | `90`                                | Rétention logs     |
| `UEBA_ENABLED`           | `True`                              | Activer UEBA        |
| `UEBA_ANOMALY_THRESHOLD` | `70`                                | Seuil d'alerte UEBA |
| `SMTP_HOST`              | *(optionnel)*                       | Serveur SMTP email  |

### Entraînement du modèle UEBA

```bash
# Sur le fichier CLUE-LDS (recommandé)
python scripts/train_ueba.py --file docs/clue.json

# Sur un échantillon (test rapide)
python scripts/train_ueba.py --file docs/clue.json --sample 500000

# Évaluer le modèle
python scripts/evaluate_ueba.py
```

---

## Tests

```bash
# Exécuter tous les tests (387 tests)
pytest -v

# Avec couverture
pytest --cov=app --cov-report=term-missing
```

### Couverture des tests

| Module                                  | Tests                 |
| --------------------------------------- | --------------------- |
| Normalisation                           | 44                    |
| Sécurité (hash, JWT, MFA)             | 18                    |
| Schémas Pydantic                       | 17                    |
| Utilitaires (rôles, permissions)       | 17                    |
| UEBA (features, scoring)                | 16                    |
| SOAR (playbooks, actions)               | 12                    |
| Notification service                    | 7                     |
| Email templating                        | 7                     |
| Corrélation (4 types + UEBA)           | 14                    |
| Repositories (alert, rule, incident...) | 78                    |
| API endpoints (auth, UEBA, logs)        | 23                    |
| Archive (Merkle, SHA-256, signature)    | 20 services + 11 repo |
| Audit (service + repo)                  | 20                    |
| **Total**                         | **387 tests**   |

---

## Pipeline UEBA

```
1. INGESTION            scripts/ingest_clue_lds.py
   CLUE-LDS (50M) → ES (logs-clue)
   
2. ENTRAÎNEMENT         scripts/train_ueba.py
   ES → extract_features() → IsolationForest → models/ueba/
   
3. SCORING TEMPS RÉEL   score_single_event()
   Log → features → compute_risk_score() → profils_ueba (PG)
   
4. CORRÉLATION          check_ueba_rule()
   score ≥ 70 → alerte → notification multi-canal
   
5. RÉ-ENTRAÎNEMENT      Celery Beat (lundi 2h)
   7 derniers jours de logs SIEM
```

---

## Licence

Projet académique — **UCAC ICAM - X3 PROJET INTÉGRATEUR**.
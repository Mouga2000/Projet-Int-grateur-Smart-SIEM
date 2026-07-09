# Smart SIEM — Frontend

Interface utilisateur de la plateforme Smart SIEM, construite avec **React 19**, **TypeScript**, **Vite** et **shadcn/ui**.

## Stack technique

| Composant | Technologie |
|-----------|------------|
| Framework | React 19 + TypeScript |
| Build | Vite 8 |
| UI | shadcn/ui (Tailwind CSS v4) |
| Routing | React Router v7 |
| HTTP | Axios |
| Graphiques | Recharts |
| State | Zustand + Context API |

## Installation

```bash
cd Frontend
npm install
npm run dev        # → http://localhost:5173
```

### Variables d'environnement

Créer un fichier `.env` à la racine de `Frontend/` :

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

| Variable | Défaut | Description |
|----------|--------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` | URL de l'API backend |

### Production (build statique)

```bash
npm run build      # → dist/
```

Les fichiers sont servis via Nginx (voir `nginx.conf`). Le Dockerfile multi-stage construit l'image pour la production.

### Déploiement

Le frontend est déployé sur **Vercel** (frontend) ou servi via **Nginx** en Docker. L'API backend est déployée sur un VPS derrière **Traefik** (HTTPS).

### Connexion Frontend ↔ Backend

Le CORS est configuré côté backend dans `SIEM/app/main.py`. Les origines autorisées incluent `http://localhost:5173` (développement) et l'URL de production.

## Structure

```
src/
├── components/     # Composants React réutilisables
│   ├── ui/         # shadcn/ui (Button, Card, Input, Table, etc.)
│   ├── logs/       # LogTable, SeverityBadge
│   ├── alerts/     # AlertTable, AlertRow, StatusBadge
│   └── layout/     # Layout, Sidebar, Navbar
├── pages/          # Pages par module
│   ├── dashboard/  # Dashboard + CrisisRoom
│   ├── logs/       # Logs + LogDetail
│   ├── alerts/     # Alertes + Détail
│   ├── investigations/ # Investigations + Détail
│   ├── admin/      # Users, Rules, Playbooks, Purge, System
│   ├── audit/      # Logs d'audit + Vérification
│   └── archive/    # Archives + Chaîne d'intégrité
├── hooks/          # useAuth, useAlerts, useWebSocket
├── services/       # API clients (axios)
├── context/        # AuthContext, AlertContext
├── config/         # ENDPOINTS, roles
├── types/          # TypeScript interfaces
└── lib/            # Utilitaires (cn)
```

## Pages et rôles

| Page | Route | Rôles |
|------|-------|-------|
| Dashboard | `/dashboard` | Analyste, RSSI, Lecteur, Admin |
| Crisis Room | `/crisis-room` | Analyste, RSSI |
| Logs | `/logs` | Analyste, Lecteur, Admin |
| Alertes | `/alerts` | Analyste, Lecteur, Admin |
| Investigations | `/investigations` | Analyste, Admin |
| Utilisateurs | `/admin/users` | Admin |
| Règles | `/admin/rules` | Admin |
| Playbooks SOAR | `/admin/playbooks` | Admin |
| Rétention | `/admin/purge` | Admin |
| Système | `/admin/system` | Admin |
| Archives | `/archive` | Admin |
| Chaîne d'intégrité | `/archive/chain` | Admin |
| Logs d'audit | `/audit/logs` | Auditeur, Admin |
| Vérification | `/audit/verify` | Auditeur, Admin |
| Profil | `/profile` | Tous |

## Endpoints SOAR (Actions)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/actions/execute?action=block-ip&agent_ip=...&ip=...` | Exécuter une action sur un agent distant |
| POST | `/api/v1/actions/notify-slack` | Notification Slack (Celery) |
| POST | `/api/v1/actions/notify-email` | Email d'alerte (Celery) |
| WS | `/api/v1/actions/ws` | Suivi temps réel des actions |

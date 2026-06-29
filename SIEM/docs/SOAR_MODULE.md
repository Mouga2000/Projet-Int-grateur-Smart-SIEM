# Module SOAR — Smart SIEM

## Architecture

```
Agent (Machine cible)                SIEM (Backend)
       │                                     │
       │ 1. Envoie les logs                   │
       │ POST /api/v1/logs/ingest            │
       │ ──────────────────────────────────►  │
       │                                     │ 2. Correlation detecte une menace
       │                                     │ 3. SOARService declenche l'action
       │                                     │
       │ 4. Appelle l'agent                  │
       │ POST /action/block-ip               │
       │ ◄────────────────────────────────── │
       │                                     │
       │ 5. Execute iptables / netsh         │
       │ 6. Retourne {"success": true}      │
       │ ──────────────────────────────────►  │
```

---

## Flux de bout en bout

```
1. Log entrant → Normalization → Elasticsearch
2. CorrelationEngine.evaluate_event() → regle declenchee
3. La regle contient actions = {"block_ip": true, "playbook_id": 1}
4. SOARService recupere l'IP de la machine cible depuis le log (host / source_ip)
5. SOARService appelle l'agent sur la machine cible
6. L'agent execute la commande locale (iptables, usermod, etc.)
7. L'agent retourne le resultat
8. SIEM journalise l'action SOAR
```

---

## Protocole de communication

### Type
- **HTTP 1.1** (pas de HTTPS en developpement)
- Pas de cle API ni d'authentification dans la version actuelle
- En production : utiliser un token JWT court ou mTLS

### Format des donnees
- **Content-Type:** `application/json`
- **Encoding:** UTF-8

### Headers

| Header | Valeur | Obligatoire |
|---|---|---|
| `Content-Type` | `application/json` | Oui |
| `Accept` | `application/json` | Oui |
| `User-Agent` | `SmartSIEM-SOAR/1.0` | Non (mais recommande pour le logging) |

### Timeout
- Le SIEM attend une reponse dans les **15 secondes** (configurable via `AGENT_TIMEOUT_SECONDS`)
- Si l'agent ne repond pas dans ce delai, le SIEM considere l'action comme echouee et passe a l'etape suivante

### Retry
- En cas d'echec (timeout ou erreur HTTP), le SIEM peut retenter l'appel selon la configuration du playbook (`max_retries`)
- Par defaut : 3 tentatives maximum

---

## Specifications techniques des endpoints agent

### Host et port
- L'agent doit ecouter sur l'IP de la machine cible, **port 9000** (configurable)
- URL de base : `http://{ip_de_la_machine}:9000`

### Endpoint 1 : Bloquer une IP

```
POST /action/block-ip
```

**Body attendu :**
```json
{
  "ip": "192.168.1.100",
  "comment": "Blocage SOAR automatique - Brute force detecte"
}
```

| Champ | Type | Description |
|---|---|---|
| `ip` | string (obligatoire) | Adresse IPv4 ou IPv6 a bloquer |
| `comment` | string (optionnel) | Commentaire pour la regle de blocage |

**Action attendue cote agent :**
- **Linux :** `iptables -A INPUT -s {ip} -j DROP`
- **Windows :** `netsh advfirewall firewall add rule name="SIEM_Block_{ip}" dir=in action=block remoteip={ip}`

---

### Endpoint 2 : Desactiver un compte

```
POST /action/disable-user
```

**Body attendu :**
```json
{
  "username": "admin",
  "reason": "Compte compromis - Brute force"
}
```

| Champ | Type | Description |
|---|---|---|
| `username` | string (obligatoire) | Nom du compte utilisateur a desactiver |
| `reason` | string (optionnel) | Raison de la desactivation |

**Action attendue cote agent :**
- **Linux :** `usermod --lock {username}` puis `chage -E 0 {username}`
- **Windows :** `net user {username} /active:no`

---

### Endpoint 3 : Isoler la machine

```
POST /action/isolate-host
```

**Body attendu :**
```json
{}
```

**Action attendue cote agent :**
- **Linux :**
  ```bash
  iptables -P INPUT DROP
  iptables -P OUTPUT DROP
  iptables -A OUTPUT -d {SIEM_SERVER_IP} -j ACCEPT  # Garder la com avec le SIEM
  ```
- **Windows :**
  ```
  netsh advfirewall firewall add rule name="SIEM_Isolate_OUT" dir=out action=block
  netsh advfirewall firewall add rule name="SIEM_Isolate_IN" dir=in action=block
  ```

---

## Reponse standard de l'agent

Tous les endpoints doivent retourner une reponse JSON au format suivant :

```json
{
  "success": true,
  "action": "block_ip",
  "detail": "IP 192.168.1.100 bloquee via iptables",
  "machine": "PC-SOPHIE",
  "timestamp": "2026-06-29T14:30:00Z"
}
```

| Champ | Type | Description |
|---|---|---|
| `success` | boolean | `true` si l'action a reussi, `false` sinon |
| `action` | string | Nom de l'action executee (`block_ip`, `disable_user`, `isolate_host`) |
| `detail` | string | Description de ce qui a ete fait ou message d'erreur |
| `machine` | string | Hostname de la machine qui a execute l'action |
| `timestamp` | string (ISO 8601) | Date et heure de l'execution |

### Codes HTTP

| Code | Signification | Action attendue du SIEM |
|---|---|---|
| `200 OK` | Action reussie | Continue le playbook |
| `400 Bad Request` | Parametres invalides | Marque l'etape comme `failed` |
| `404 Not Found` | Endpoint inexistant | Interrompt le playbook |
| `500 Internal Server Error` | Erreur lors de l'execution | Retry selon `max_retries` |
| `503 Service Unavailable` | Agent surcharge | Retry |

---

## Securite

### Version actuelle (developpement)
- **Pas d'authentification** entre le SIEM et l'agent
- Communication en HTTP (pas de TLS)
- L'agent est accessible sur le reseau local uniquement

### Recommandations production
- Ajouter un token JWT court expire dans les 30 secondes
- Passer en HTTPS avec certificats auto-signes
- Ajouter une whitelist d'IP autorisees a contacter l'agent
- Utiliser un port different du 9000 (ex: 9443)

---

## Configuration reseau

### Ce que l'agent doit ouvrir

| Sens | Port | Protocole | Description |
|---|---|---|---|
| Entrant | 9000 | TCP | Reception des commandes SOAR depuis le SIEM |

### Ce que le SIEM doit pouvoir joindre
- L'IP de chaque machine cible sur le port 9000
- Si les machines sont sur des sous-reseaux differents, s'assurer que le routage est en place

---

## Journalisation cote agent

L'agent doit logger chaque action recue et son resultat. Format attendu :

```
[2026-06-29 14:30:00] ACTION block_ip FROM 10.0.0.10: IP 192.168.1.100 → SUCCESS
[2026-06-29 14:30:05] ACTION disable-user FROM 10.0.0.10: admin → FAILED (user not found)
```

---

## Lancement de l'agent

L'agent doit etre lance avec cette configuration minimale :

```bash
# Variables d'environnement requises
export AGENT_PORT=9000
export SIEM_SERVER_IP=10.0.0.10   # IP du serveur SIEM (utilisee pour l'isolation)

# Lancement
python agent/main.py
```

**Sous Windows :**
```cmd
set AGENT_PORT=9000
python agent\main.py
```

---

## Exemple de code minimal cote agent (FastAPI)

```python
# agent/main.py
# A developper par ton collegue

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import platform
import subprocess

app = FastAPI(title="SIEM Agent", version="1.0.0")


class BlockIPRequest(BaseModel):
    ip: str
    comment: Optional[str] = None


class DisableUserRequest(BaseModel):
    username: str
    reason: Optional[str] = None


class ActionResult(BaseModel):
    success: bool
    action: str
    detail: str
    machine: str = platform.node()
    timestamp: str = datetime.now(timezone.utc).isoformat()


@app.post("/action/block-ip")
async def block_ip(data: BlockIPRequest):
    try:
        subprocess.run(["iptables", "-A", "INPUT", "-s", data.ip, "-j", "DROP"],
                       check=True, timeout=10)
        return ActionResult(success=True, action="block_ip",
                            detail=f"IP {data.ip} bloquee")
    except Exception as e:
        return ActionResult(success=False, action="block_ip",
                            detail=str(e))


@app.post("/action/disable-user")
async def disable_user(data: DisableUserRequest):
    try:
        subprocess.run(["usermod", "--lock", data.username], check=True, timeout=10)
        return ActionResult(success=True, action="disable_user",
                            detail=f"Compte {data.username} verrouille")
    except Exception as e:
        return ActionResult(success=False, action="disable_user",
                            detail=str(e))


@app.post("/action/isolate-host")
async def isolate_host():
    try:
        subprocess.run(["iptables", "-P", "INPUT", "DROP"], check=True, timeout=10)
        subprocess.run(["iptables", "-P", "OUTPUT", "DROP"], check=True, timeout=10)
        return ActionResult(success=True, action="isolate_host",
                            detail="Trafic entrant/sortant bloque")
    except Exception as e:
        return ActionResult(success=False, action="isolate_host",
                            detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok", "hostname": platform.node()}


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("AGENT_PORT", "9000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

---

## Comment le SIEM appelle l'agent (code cote SIEM)

```python
# Extrait de app/services/soar.py

async def _call_agent(self, agent_ip: str, action: str, payload: dict) -> dict:
    """
    Appelle l'agent sur la machine cible.

    Args:
        agent_ip: IP ou hostname de la machine cible
        action: 'block-ip', 'disable-user', 'isolate-host'
        payload: donnees a envoyer a l'agent

    Returns:
        dict avec success, action, detail
    """
    if not agent_ip:
        return {"success": False, "action": action, "error": "IP agent manquante"}

    url = f"http://{agent_ip}:{settings.AGENT_DEFAULT_PORT}/action/{action}"

    async with httpx.AsyncClient(timeout=settings.AGENT_TIMEOUT_SECONDS) as client:
        try:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                return response.json()
            return {
                "success": False, "action": action,
                "error": f"HTTP {response.status_code}: {response.text}",
            }
        except httpx.ConnectError:
            return {"success": False, "action": action, "error": f"Agent {url} injoignable"}
        except httpx.TimeoutException:
            return {"success": False, "action": action, "error": "Timeout agent"}
```

---

## Test manuel de l'agent

Une fois l'agent lance, le SIEM peut le tester avec curl :

```bash
# Tester que l'agent repond
curl http://{ip_machine}:9000/health

# Tester le blocage IP
curl -X POST http://{ip_machine}:9000/action/block-ip \
  -H "Content-Type: application/json" \
  -d '{"ip": "10.0.0.99"}'

# Tester la desactivation de compte
curl -X POST http://{ip_machine}:9000/action/disable-user \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser"}'

# Tester l'isolation
curl -X POST http://{ip_machine}:9000/action/isolate-host \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## Endpoints API (cote SIEM)

### Playbooks (CRUD + execution)

| Methode | URL | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/playbooks/` | Token | Lister les playbooks |
| `POST` | `/api/v1/playbooks/` | Admin | Creer un playbook |
| `GET` | `/api/v1/playbooks/{id}` | Token | Detail d'un playbook |
| `PUT` | `/api/v1/playbooks/{id}` | Admin | Modifier un playbook |
| `DELETE` | `/api/v1/playbooks/{id}` | Admin | Supprimer un playbook |
| `POST` | `/api/v1/playbooks/{id}/execute` | Analyste/Admin | Executer un playbook |

---

## Structure d'un playbook

```json
{
  "name": "Bloquer IP malveillante",
  "description": "Bloque une IP source via le pare-feu systeme",
  "trigger": "manual",
  "enabled": true,
  "steps": [
    {
      "action": "block_ip",
      "params": {
        "ip": "{{source_ip}}"
      }
    },
    {
      "action": "notify_slack",
      "params": {
        "channel": "#security",
        "message": "IP {{source_ip}} bloquee"
      }
    }
  ],
  "timeout_seconds": 300,
  "max_retries": 3
}
```

### Actions disponibles

| Action | Description | Parametres |
|---|---|---|
| `block_ip` | Bloquer une IP sur la machine cible | `ip`, `comment` |
| `disable_user` | Desactiver un compte local | `username` |
| `isolate_host` | Isoler la machine du reseau | `hostname` |
| `notify_slack` | Envoyer une notification Slack | `channel`, `message` |
| `notify_email` | Envoyer un email | `to`, `subject`, `body` |
| `create_ticket` | Creer un ticket (placeholder) | `title`, `description` |

---

## Fichiers cote SIEM

| Fichier | Role |
|---|---|
| `app/models/sql_models.py` | Table `Agent` + modele `Playbook` (existant) |
| `app/repositories/playbook_repo.py` | CRUD playbooks PostgreSQL |
| `app/services/soar.py` | Service SOAR (appelle l'agent) |
| `app/api/v1/playbooks.py` | Endpoints CRUD + execution |
| `app/api/v1/router.py` | Routeur branche |
| `scripts/seed_playbooks.py` | 3 playbooks par defaut |
| `.env` | Configuration des agents |

---

## Configuration dans `.env`

```env
# Agents SIEM (pour le module SOAR)
AGENT_DEFAULT_PORT=9000
AGENT_TIMEOUT_SECONDS=15
```

---

## Dependances

- `httpx` — pour appeler l'agent en HTTP asynchrone

```bash
pip install httpx
```

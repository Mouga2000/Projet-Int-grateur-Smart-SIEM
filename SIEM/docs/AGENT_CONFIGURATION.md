# Configuration de l'Agent SOAR

## 1. Informations nécessaires

L'agent a besoin de **5 éléments** pour fonctionner :

| # | Info                                | Méthode d'obtention                        | Exemple                                      |
| - | ----------------------------------- | ------------------------------------------- | -------------------------------------------- |
| 1 | **URL du serveur WebSocket**  | Configuration manuelle                      | `ws://192.168.1.100:8000/api/v1/agents/ws` |
| 2 | **Hostname**                  | `platform.node()` (automatique)           | `PC-SOPHIE`                                |
| 3 | **Adresse IP**                | IP locale de la machine (automatique)       | `192.168.1.10`                             |
| 4 | **Système d'exploitation**   | `platform.system().lower()` (automatique) | `linux` ou `windows`                     |
| 5 | **Commandes OS à exécuter** | Selon l'OS (intégré dans le code)         | `iptables`, `netsh`, `usermod`...      |

---

## 2. URL de connexion

```
ws://<IP_DU_SERVEUR_SIEM>:8000/api/v1/agents/ws
```

C'est la **seule donnée de configuration externe** à fournir à l'agent.

---

## 3. Protocole de communication

### 3.1 Enregistrement

```
Agent → Serveur :
{
  "type": "register",
  "hostname": "PC-SOPHIE",
  "ip": "192.168.1.10",
  "os": "linux"
}

Serveur → Agent :
{
  "type": "registered",
  "agent_id": "agent-abc123"
}
```

### 3.2 Réception d'une commande

```
Serveur → Agent :
{
  "type": "command",
  "action_id": "a1b2c3d4",
  "action": "block-ip",
  "params": {
    "ip": "10.0.0.5",
    "duration": 3600
  }
}

Agent → Serveur (après exécution) :
{
  "type": "result",
  "action_id": "a1b2c3d4",
  "result": {
    "success": true,
    "action": "block_ip",
    "detail": "IP 10.0.0.5 bloquee via iptables",
    "machine": "PC-SOPHIE",
    "timestamp": "2026-07-03T10:00:00Z"
  }
}
```

### 3.3 Keepalive (toutes les 30s)

```
Agent → Serveur : { "type": "ping" }
Serveur → Agent : { "type": "pong" }
```

---

## 4. Actions et commandes système

### 4.1 block-ip

Bloque une adresse IP sur la machine via le pare-feu local.

| Élément                   | Valeur                       |
| --------------------------- | ---------------------------- |
| **action**            | `block-ip`                 |
| **params requis**     | `ip` (string)              |
| **params optionnels** | `duration` (int, secondes) |

**Linux :**

```bash
iptables -A INPUT -s {ip} -j DROP
```

**Windows :**

```cmd
netsh advfirewall firewall add rule name="SIEM_Block_{ip}" dir=in action=block remoteip={ip}
```

### 4.2 disable-user

Désactive un compte utilisateur sur la machine.

| Élément               | Valeur                |
| ----------------------- | --------------------- |
| **action**        | `disable-user`      |
| **params requis** | `username` (string) |

**Linux :**

```bash
usermod --lock {username}
chage -E 0 {username}
```

**Windows :**

```cmd
net user {username} /active:no
```

### 4.3 isolate-host

Isole la machine du réseau en bloquant tout le trafic entrant/sortant.

| Élément               | Valeur           |
| ----------------------- | ---------------- |
| **action**        | `isolate-host` |
| **params requis** | Aucun            |

**Linux :**

```bash
iptables -P INPUT DROP
iptables -P OUTPUT DROP
# Garder la communication avec le serveur SIEM
iptables -A OUTPUT -d {SIEM_SERVER_IP} -j ACCEPT
```

**Windows :**

```cmd
netsh advfirewall firewall add rule name="SIEM_Isolate_OUT" dir=out action=block
netsh advfirewall firewall add rule name="SIEM_Isolate_IN" dir=in action=block
```

---

## 5. Réponse standard

Toutes les actions doivent retourner :

```json
{
  "success": true,
  "action": "block_ip",
  "detail": "IP 10.0.0.5 bloquee via iptables",
  "machine": "PC-SOPHIE",
  "timestamp": "2026-07-03T10:00:00Z"
}
```

| Champ         | Type            | Description                          |
| ------------- | --------------- | ------------------------------------ |
| `success`   | bool            | `true` si réussi, `false` sinon |
| `action`    | string          | Nom de l'action exécutée           |
| `detail`    | string          | Description ou message d'erreur      |
| `machine`   | string          | Hostname de la machine               |
| `timestamp` | string ISO 8601 | Date et heure d'exécution           |

---

## 6. Gestion des erreurs

| Situation                     | Action de l'agent                                                       |
| ----------------------------- | ----------------------------------------------------------------------- |
| **Connexion perdue**    | Attendre 5s,**reconnecter** automatiquement                       |
| **Commande inconnue**   | Répondre`{"success": false, "error": "Action inconnue"}`             |
| **Commande échouée**  | Répondre`{"success": false, "error": "message d'erreur"}`            |
| **Permission refusée** | Répondre`{"success": false, "error": "iptables: Permission denied"}` |
| **Timeout serveur**     | L'agent doit quand même répondre (le serveur attend 15s max)          |

### Codes HTTP et comportement attendu

| Code                   | Situations       | Action du SIEM                           |
| ---------------------- | ---------------- | ---------------------------------------- |
| Connexion WS établie  | Agent en ligne   | Envoie les commandes                     |
| Connexion WS perdue    | Agent hors ligne | Marque l'action comme`failed`          |
| Pas de réponse en 15s | Timeout          | Retente selon`max_retries` du playbook |

---

## 7. Démarrage de l'agent

```bash
# Linux / macOS
export SIEM_WS_URL="ws://192.168.1.100:8000/api/v1/agents/ws"
python agent/main.py

# Windows (cmd)
set SIEM_WS_URL=ws://192.168.1.100:8000/api/v1/agents/ws
python agent\main.py
```

L'agent doit :

1. Se connecter au WebSocket
2. S'enregistrer avec ses informations
3. Rester en écoute des commandes
4. Exécuter les actions et répondre
5. Envoyer des `ping` réguliers (toutes les 30s)
6. Se reconnecter automatiquement en cas de perte de connexion

# app/services/agent_ws.py
# -------------------------------
# Gestionnaire de connexions WebSocket pour les agents SOAR.
#
# Les agents se connectent AU SERVEUR via WebSocket (au lieu du serveur
# qui les contacte en HTTP). Cela evite d'ouvrir un port sur l'agent
# et fonctionne a travers les NAT / pare-feux.
#
# Protocole :
#   1. Agent → Serveur : { "type": "register",   "hostname": "PC-01", "ip": "192.168.1.10" }
#   2. Serveur → Agent : { "type": "registered", "agent_id": "agent-xxx" }
#   3. Serveur → Agent : { "type": "command",    "action_id": "...", "action": "block-ip",
#                          "params": { "ip": "10.0.0.5" } }
#   4. Agent → Serveur : { "type": "result",     "action_id": "...",
#                          "result": { "success": true, "detail": "IP bloquee" } }
#   5. Agent → Serveur : { "type": "ping" }
#   6. Serveur → Agent : { "type": "pong" }

import asyncio
import uuid
from typing import Optional

from fastapi import WebSocket


class AgentWSManager:
    """
    Gere les connexions WebSocket des agents et permet d'envoyer
    des commandes en attendant leur reponse de maniere asynchrone.
    """

    def __init__(self):
        # { hostname: WebSocket }
        self._connections: dict[str, WebSocket] = {}
        # { hostname: { "ip": ..., "os": ..., "connected_at": ... } }
        self._infos: dict[str, dict] = {}
        # { action_id: asyncio.Future } pour attendre les reponses
        self._pending: dict[str, asyncio.Future] = {}

    # ------------------------------------------------------------------
    # Gestion des connexions
    # ------------------------------------------------------------------

    async def register(
        self, ws: WebSocket, hostname: str, info: dict
    ) -> str:
        """
        Enregistre un agent connecte via WebSocket.

        Retourne un agent_id unique.
        """
        agent_id = f"agent-{uuid.uuid4().hex[:6]}"
        self._connections[hostname] = ws
        self._infos[hostname] = {
            "agent_id": agent_id,
            "ip": info.get("ip", ""),
            "os": info.get("os", ""),
            "connected_at": info.get("connected_at", ""),
        }
        return agent_id

    async def unregister(self, hostname: str):
        """Retire un agent deconnecte."""
        self._connections.pop(hostname, None)
        self._infos.pop(hostname, None)
        # Annuler les futures en attente pour cet agent
        to_remove = []
        for action_id, future in self._pending.items():
            if not future.done():
                future.set_exception(
                    ConnectionError(f"Agent {hostname} deconnecte")
                )
                to_remove.append(action_id)
        for aid in to_remove:
            self._pending.pop(aid, None)

    def is_connected(self, hostname: str) -> bool:
        """Verifie si un agent est connecte via WebSocket."""
        return hostname in self._connections

    def get_connected_agents(self) -> list[dict]:
        """Retourne la liste des agents connectes."""
        return [
            {"hostname": h, **v}
            for h, v in self._infos.items()
        ]

    def get_hostname_by_ip(self, ip: str) -> Optional[str]:
        """
        Retrouve le hostname d'un agent a partir de son IP.
        Utilise par _call_agent pour choisir entre WS et HTTP.
        """
        for hostname, info in self._infos.items():
            if info.get("ip") == ip:
                return hostname
        return None

    def get_ws(self, hostname: str) -> Optional[WebSocket]:
        """Retourne la WebSocket d'un agent."""
        return self._connections.get(hostname)

    # ------------------------------------------------------------------
    # Envoi de commandes
    # ------------------------------------------------------------------

    async def send_command(
        self,
        hostname: str,
        action: str,
        params: dict,
        timeout: int = 15,
    ) -> dict:
        """
        Envoie une commande a un agent via WebSocket et attend la reponse.

        Args:
            hostname: nom de l'agent cible
            action: 'block-ip', 'disable-user', 'isolate-host'
            params: parametres de l'action
            timeout: delai d'attente max en secondes

        Retourne:
            dict avec success, action, detail, etc.
        """
        ws = self._connections.get(hostname)
        if not ws:
            return {
                "success": False,
                "action": action,
                "error": f"Agent {hostname} non connecte",
            }

        action_id = str(uuid.uuid4())[:8]
        future = asyncio.get_event_loop().create_future()
        self._pending[action_id] = future

        try:
            # Envoyer la commande a l'agent
            await ws.send_json({
                "type": "command",
                "action_id": action_id,
                "action": action,
                "params": params,
            })

            # Attendre la reponse (avec timeout)
            result = await asyncio.wait_for(future, timeout=timeout)
            return result

        except asyncio.TimeoutError:
            self._pending.pop(action_id, None)
            return {
                "success": False,
                "action": action,
                "error": f"Timeout ({timeout}s) - Agent {hostname}",
            }
        except ConnectionError as e:
            self._pending.pop(action_id, None)
            return {
                "success": False,
                "action": action,
                "error": str(e),
            }

    # ------------------------------------------------------------------
    # Traitement des messages entrants
    # ------------------------------------------------------------------

    async def handle_message(self, ws: WebSocket, data: dict):
        """
        Traite un message recu d'un agent.

        - 'result' → resolve la future en attente
        - 'ping'   → repond 'pong'
        """
        msg_type = data.get("type")

        if msg_type == "result":
            action_id = data.get("action_id")
            future = self._pending.get(action_id)
            if future and not future.done():
                future.set_result(data.get("result", {}))
            return

        if msg_type == "ping":
            try:
                await ws.send_json({"type": "pong"})
            except Exception:
                pass
            return


# Instance unique partagee dans toute l'application
agent_ws_manager = AgentWSManager()

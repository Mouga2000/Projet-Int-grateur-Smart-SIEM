# app/services/soar.py
# -------------------------------
# Service SOAR : orchestration des actions sur les agents distants
#
# Pour contacter un agent, le service utilise d'abord le WebSocket
# si l'agent est connecte, sinon il tombe en repli HTTP.

import re
from typing import Optional

import httpx

from app.core.config import settings
from app.repositories.playbook_repo import PlaybookRepository
from app.services.agent_ws import agent_ws_manager
from app.tasks.notification_tasks import (
    send_email_notification,
    send_slack_notification,
)


def _resolve_template(value, context: dict):
    """
    Remplace les variables {{var}} par les valeurs du contexte.
    Exemple : "{{source_ip}}" → "10.0.0.5"
    """
    if isinstance(value, str):
        for key, val in context.items():
            value = value.replace("{{" + key + "}}", str(val) if val else "")
    return value


def _resolve_params(params: dict, context: dict) -> dict:
    """Applique _resolve_template sur tous les valeurs d'un dict de parametres."""
    return {k: _resolve_template(v, context) for k, v in params.items()}


class SOARService:
    """
    Service SOAR : envoie des commandes aux agents distants
    pour executer des actions de remediation (blocage IP,
    desactivation compte, isolation machine).
    """

    def __init__(self, playbook_repo: PlaybookRepository):
        self.playbook_repo = playbook_repo

    # ----------------------------------------------------------
    # Execution d'un playbook complet
    # ----------------------------------------------------------

    async def execute_playbook(self, playbook_id: int, context: dict) -> dict:
        """Execute un playbook avec son contexte (alerte, IP, host)."""
        playbook = await self.playbook_repo.get_by_id(playbook_id)
        if not playbook:
            return {"success": False, "error": "Playbook non trouve"}

        results = []
        for step in playbook.get("steps", []):
            step_result = await self.execute_step(step, context)
            results.append(step_result)
            # Retry si echec
            if not step_result["success"] and playbook.get("max_retries", 0) > 0:
                for _ in range(playbook["max_retries"]):
                    step_result = await self.execute_step(step, context)
                    results.append(step_result)
                    if step_result["success"]:
                        break

        await self.playbook_repo.increment_execution(playbook_id)
        all_ok = all(r["success"] for r in results)
        return {
            "success": all_ok,
            "playbook": playbook["name"],
            "results": results,
        }

    async def execute_step(self, step: dict, context: dict) -> dict:
        """Execute une action individuelle du playbook."""
        action = step.get("action", "")
        params = _resolve_params(step.get("params", {}), context)
        agent_ip = context.get("agent_ip") or context.get("host")

        try:
            if action == "block_ip":
                ip = params.get("ip") or context.get("source_ip")
                return await self._call_agent(agent_ip, "block-ip", {"ip": ip})

            elif action == "disable_user":
                username = params.get("username") or context.get("user")
                return await self._call_agent(
                    agent_ip, "disable-user", {"username": username}
                )

            elif action == "isolate_host":
                return await self._call_agent(agent_ip, "isolate-host", {})

            elif action == "notify_slack":
                send_slack_notification.delay(
                    params.get("channel", "#security"),
                    params.get("message", "Action SOAR declenchee"),
                )
                return {"success": True, "action": action}

            elif action == "notify_email":
                send_email_notification.delay(
                    params["to"],
                    params.get("subject", "Alerte SIEM"),
                    params.get("body", "Action SOAR executee"),
                )
                return {"success": True, "action": action}

            elif action == "create_ticket":
                ticket_id = f"SIEM-{abs(hash(params.get('title', ''))) % 100000:05d}"
                return {"success": True, "action": action, "ticket_id": ticket_id}

            else:
                return {
                    "success": False,
                    "action": action,
                    "error": f"Action inconnue: {action}",
                }

        except Exception as e:
            return {"success": False, "action": action, "error": str(e)}

    # ----------------------------------------------------------
    # Appel a l'agent distant
    # ----------------------------------------------------------

    async def _call_agent(self, agent_ip: str, action: str, payload: dict) -> dict:
        """
        Appelle l'agent sur la machine cible.

        Priorise le WebSocket (connexion persistante initiee par l'agent).
        Si l'agent n'est pas connecte en WS, tombe en repli HTTP.

        Args:
            agent_ip: IP ou hostname de la machine cible
            action: 'block-ip', 'disable-user', 'isolate-host'
            payload: donnees a envoyer a l'agent

        Returns:
            dict avec success, action, detail
        """
        if not agent_ip:
            return {"success": False, "action": action, "error": "IP agent manquante"}

        # ---- 1. Tentative WebSocket ----
        hostname = agent_ws_manager.get_hostname_by_ip(agent_ip)
        if hostname and agent_ws_manager.is_connected(hostname):
            return await agent_ws_manager.send_command(
                hostname=hostname,
                action=action,
                params=payload,
                timeout=settings.AGENT_TIMEOUT_SECONDS,
            )

        # ---- 2. Repli HTTP ----
        url = f"http://{agent_ip}:{settings.AGENT_DEFAULT_PORT}/action/{action}"

        async with httpx.AsyncClient(timeout=settings.AGENT_TIMEOUT_SECONDS) as client:
            try:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    return response.json()
                return {
                    "success": False,
                    "action": action,
                    "error": f"HTTP {response.status_code}: {response.text}",
                }
            except httpx.ConnectError:
                return {
                    "success": False,
                    "action": action,
                    "error": f"Agent {url} injoignable",
                }
            except httpx.TimeoutException:
                return {"success": False, "action": action, "error": "Timeout agent"}

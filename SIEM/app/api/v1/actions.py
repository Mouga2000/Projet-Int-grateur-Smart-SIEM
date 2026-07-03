# app/api/v1/actions.py
# -------------------------------
# Endpoints directs pour les actions SOAR.
#
# FLOW ASYNCHRONE :
#   1. Frontend appelle GET /actions/execute?action=...&param=...
#   2. Backend retourne IMMEDIATEMENT un action_id + status "running"
#   3. Backend execute l'action en ARRIERE-PLAN (asyncio.create_task)
#   4. Le resultat est envoye en temps reel via WebSocket
#
# Suivi en temps reel via WebSocket :
#   WS /api/v1/actions/ws

import asyncio
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.api.dependencies import require_role
from app.core.database import async_session_factory
from app.repositories.playbook_repo import PlaybookRepository
from app.services.soar import SOARService
from app.tasks.notification_tasks import (
    send_email_notification,
    send_slack_notification,
)
from app.utils.tags import Role

router = APIRouter(prefix="/actions", tags=["Actions SOAR"])


# =============================================================================
# WebSocket Connection Manager
# =============================================================================


class ConnectionManager:
    """Gerer les connexions WebSocket pour le suivi des actions en temps reel."""

    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, event: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(event)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


ws_manager = ConnectionManager()


# =============================================================================
# Helpers
# =============================================================================


async def _broadcast_action(action: str, action_id: str, status: str, **extra):
    """Emet un evenement WebSocket."""
    await ws_manager.broadcast({
        "type": "action_update",
        "action": action,
        "id": action_id,
        "status": status,
        **extra,
    })


async def _run_agent_action(
    action_id: str,
    action_name: str,
    params: dict,
    context: dict,
    target_label: str,
    agent_ip: str,
):
    """
    Execute une action agent en ARRIERE-PLAN.
    Cree sa propre session DB et broadcast le resultat via WebSocket.
    """
    try:
        async with async_session_factory() as db:
            repo = PlaybookRepository(db)
            soar = SOARService(repo)
            step = {"action": action_name, "params": params}
            result = await soar.execute_step(step, context)

        status = "completed" if result.get("success") else "failed"
        await _broadcast_action(
            action_name, action_id, status,
            target=target_label, agent=agent_ip, result=result,
        )
    except Exception as e:
        await _broadcast_action(
            action_name, action_id, "failed",
            target=target_label, agent=agent_ip, error=str(e),
        )


# =============================================================================
# Actions autorisees et leurs parametres requis
# =============================================================================

ACTIONS_MAP = {
    "block-ip": {
        "action_name": "block_ip",
        "params": ["ip"],
        "opt_params": ["duration"],
        "target_label": lambda p: p.get("ip", ""),
    },
    "disable-user": {
        "action_name": "disable_user",
        "params": ["username"],
        "opt_params": [],
        "target_label": lambda p: p.get("username", ""),
    },
    "isolate-host": {
        "action_name": "isolate_host",
        "params": [],
        "opt_params": ["host"],
        "target_label": lambda p: p.get("host", ""),
    },
}


# =============================================================================
# Endpoint unique pour toutes les actions agent
# =============================================================================


@router.get("/execute")
async def execute_action(
    action: str = Query(..., description="Action a executer : block-ip, disable-user, isolate-host"),
    agent_ip: str = Query(..., description="IP de l'agent qui execute l'action"),
    ip: Optional[str] = Query(None, description="IP a bloquer (pour block-ip)"),
    username: Optional[str] = Query(None, description="Utilisateur a desactiver (pour disable-user)"),
    host: Optional[str] = Query(None, description="Machine a isoler (pour isolate-host)"),
    duration: Optional[int] = Query(None, description="Duree du blocage en secondes (optionnel)"),
    current_user: dict = Depends(require_role([Role.ANALYSTE, Role.ADMINISTRATEUR])),
):
    """
    Execute une action SOAR sur un agent distant.

    Retourne immediatement. Le resultat arrive en temps reel via WebSocket.

    **Exemples :**
    - `GET /actions/execute?action=block-ip&agent_ip=192.168.1.10&ip=10.0.0.5`
    - `GET /actions/execute?action=disable-user&agent_ip=192.168.1.10&username=jdupont`
    - `GET /actions/execute?action=isolate-host&agent_ip=192.168.1.10&host=PC-01`
    """
    # Valider l'action
    action_def = ACTIONS_MAP.get(action)
    if not action_def:
        valid = ", ".join(ACTIONS_MAP.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Action '{action}' inconnue. Actions valides : {valid}",
        )

    # Valider les parametres requis
    all_params = {
        "ip": ip,
        "username": username,
        "host": host,
        "duration": duration,
    }
    for req_param in action_def["params"]:
        if not all_params.get(req_param):
            raise HTTPException(
                status_code=400,
                detail=f"Parametre requis manquant pour '{action}' : '{req_param}'",
            )

    # Construire les params et le contexte
    action_name = action_def["action_name"]
    step_params = {k: v for k, v in all_params.items() if v is not None}
    context = {"agent_ip": agent_ip}
    target_label = action_def["target_label"](step_params)

    # Lancer l'action
    action_id = str(uuid.uuid4())[:8]

    await _broadcast_action(
        action_name, action_id, "running",
        target=target_label, agent=agent_ip,
    )

    asyncio.create_task(_run_agent_action(
        action_id=action_id,
        action_name=action_name,
        params=step_params,
        context=context,
        target_label=target_label,
        agent_ip=agent_ip,
    ))

    return {
        "action_id": action_id,
        "action": action_name,
        "status": "running",
        "target": target_label,
        "agent": agent_ip,
        "message": "Action lancee. Suivez le resultat en temps reel via WebSocket ws://.../actions/ws",
    }


# =============================================================================
# Notifications (POST — taches Celery asynchrones)
# =============================================================================


class SlackNotifyRequest(BaseModel):
    channel: str = "#security"
    message: str


class EmailNotifyRequest(BaseModel):
    to: str
    subject: str = "Alerte SIEM"
    body: str


@router.post("/notify-slack")
async def notify_slack(
    req: SlackNotifyRequest,
    current_user: dict = Depends(require_role([Role.ANALYSTE, Role.ADMINISTRATEUR])),
):
    """Envoie une notification Slack via Celery."""
    action_id = str(uuid.uuid4())[:8]

    await _broadcast_action("notify_slack", action_id, "running", target=req.channel)
    send_slack_notification.delay(req.channel, req.message)

    result = {"success": True, "action": "notify_slack"}
    await _broadcast_action("notify_slack", action_id, "completed", result=result)
    return {"action_id": action_id, **result}


@router.post("/notify-email")
async def notify_email(
    req: EmailNotifyRequest,
    current_user: dict = Depends(require_role([Role.ANALYSTE, Role.ADMINISTRATEUR])),
):
    """Envoie un email d'alerte via Celery."""
    action_id = str(uuid.uuid4())[:8]

    await _broadcast_action("notify_email", action_id, "running", target=req.to)
    send_email_notification.delay(req.to, req.subject, {"description": req.body})

    result = {"success": True, "action": "notify_email"}
    await _broadcast_action("notify_email", action_id, "completed", result=result)
    return {"action_id": action_id, **result}


# =============================================================================
# WebSocket pour le suivi en temps reel
# =============================================================================


@router.websocket("/ws")
async def actions_websocket(websocket: WebSocket):
    """
    WebSocket pour recevoir les mises a jour en temps reel des actions SOAR.

    Exemple de message recu :
    ```json
    {"type": "action_update", "action": "block_ip", "id": "a1b2c3d4",
     "status": "running", "target": "10.0.0.5", "agent": "192.168.1.10"}
    ```
    """
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)

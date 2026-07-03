# app/api/v1/agents.py
# -------------------------------
# Endpoints /api/v1/agents — Gestion des agents SOAR
#
# Les agents se connectent au serveur via WebSocket (WS /agents/ws)
# pour recevoir les commandes SOAR en temps reel.
# Le serveur n'a pas besoin d'appeler l'agent en HTTP :
# la connexion persistante WS permet d'envoyer les ordres
# et de recevoir les resultats.

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_role
from app.core.database import get_db
from app.repositories.agent_repo import AgentRepository
from app.services.agent_ws import agent_ws_manager
from app.utils.tags import Role

router = APIRouter(prefix="/agents", tags=["Agents SOAR"])


class AgentRegisterRequest(BaseModel):
    hostname: str = Field(..., min_length=1, max_length=255)
    ip_address: str = Field(..., min_length=7, max_length=45)
    agent_port: int = Field(default=9000, ge=1, le=65535)
    operating_system: str = Field(default="", max_length=50)


@router.post("/register", status_code=201)
async def register_agent(
    data: AgentRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Point d'entrée pour l'auto-enregistrement des agents SOAR.

    Appelé par l'agent au démarrage pour s'enregistrer dans la base.
    L'agent envoie son hostname, IP, port et OS.
    Si l'agent existe déjà (même hostname), son IP et son statut sont mis à jour.
    """
    repo = AgentRepository(db)
    agent = await repo.register(
        hostname=data.hostname,
        ip_address=data.ip_address,
        agent_port=data.agent_port,
        operating_system=data.operating_system or None,
    )
    return agent


@router.get("/")
async def list_agents(
    current_user: dict = Depends(require_role([Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """Liste les agents SOAR actifs (base de données)."""
    repo = AgentRepository(db)
    return await repo.list_active()


@router.get("/connected")
async def list_connected_agents(
    current_user: dict = Depends(require_role([Role.ADMINISTRATEUR])),
):
    """
    Liste les agents actuellement connectés via WebSocket.
    Utile pour savoir quels agents sont joignables en temps réel.
    """
    return agent_ws_manager.get_connected_agents()


# =============================================================================
# WebSocket — Connexion persistante des agents
# =============================================================================
# Les agents se connectent ici et reçoivent les commandes SOAR.
# Protocole :
#   1. Agent envoie : { "type": "register", "hostname": "PC-01", "ip": "192.168.1.10", "os": "linux" }
#   2. Serveur répond : { "type": "registered", "agent_id": "agent-abc123" }
#   3. Serveur envoie : { "type": "command", "action_id": "...", "action": "block-ip",
#                         "params": { "ip": "10.0.0.5" } }
#   4. Agent répond : { "type": "result", "action_id": "...",
#                       "result": { "success": true, "detail": "IP bloquee" } }


@router.websocket("/ws")
async def agent_websocket(websocket: WebSocket):
    """
    Point de connexion WebSocket pour les agents SOAR.

    L'agent doit d'abord s'enregistrer en envoyant :
        { "type": "register", "hostname": "PC-01", "ip": "192.168.1.10", "os": "linux" }

    Ensuite, le serveur peut lui envoyer des commandes :
        { "type": "command", "action_id": "...", "action": "block-ip",
          "params": { "ip": "10.0.0.5" } }

    L'agent execute et repond :
        { "type": "result", "action_id": "...",
          "result": { "success": true, "detail": "IP bloquee" } }
    """
    await websocket.accept()
    hostname = None

    try:
        while True:
            raw = await websocket.receive_json()
            msg_type = raw.get("type")

            if msg_type == "register":
                hostname = raw.get("hostname", "")
                ip = raw.get("ip", "")
                os_name = raw.get("os", "")

                if not hostname:
                    await websocket.send_json({
                        "type": "error",
                        "message": "hostname requis",
                    })
                    continue

                agent_id = await agent_ws_manager.register(
                    ws=websocket,
                    hostname=hostname,
                    info={
                        "ip": ip,
                        "os": os_name,
                        "connected_at": datetime.now(timezone.utc).isoformat(),
                    },
                )
                await websocket.send_json({
                    "type": "registered",
                    "agent_id": agent_id,
                })

            elif msg_type == "result":
                # Resultat d'une commande, transmis au gestionnaire
                await agent_ws_manager.handle_message(websocket, raw)

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

            else:
                # Autres messages (logs, heartbeat…) transmis au gestionnaire
                await agent_ws_manager.handle_message(websocket, raw)

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        if hostname:
            agent_ws_manager.unregister(hostname)

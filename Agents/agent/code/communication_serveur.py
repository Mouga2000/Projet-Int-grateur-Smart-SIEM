"""
Réception des commandes SOAR via WebSocket.
"""

import json
import threading
import time
import socket
import platform
import uuid
from datetime import datetime, UTC
from websocket import WebSocketApp

from code.config import Config
from code.logger import AgentLogger

from code.actions.block_ip import BlockIPAction
from code.actions.disable_user import DisableUserAction
from code.actions.isolate_host import IsolateHostAction

from code.communication import CommunicationClient



def get_local_ip() -> str:
    try:
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return "127.0.0.1"






class CommandService:

    def __init__(self):

        self.config = Config()
        self.logger = AgentLogger().get_logger()
        self.client = CommunicationClient()

        server = self.config.get("server")

        protocol = "wss" if server["protocol"] == "https" else "ws"

        self.ws_url = (
            f"{protocol}://"
            f"{server['host']}:"
            f"{server['port']}"
            f"{server['api']['ws_commands']}"
        )

        self.agent_id = self.config.get("agent", "id")

        self.actions = {
            "block-ip": BlockIPAction(),
            "disable-user": DisableUserAction(),
            "isolate-host": IsolateHostAction()
        }

        self.ws = None




    def start(self):
        thread = threading.Thread(
            target=self._run,
            daemon=True
        )
        self.logger.info("Demarage du WebSocket")
        thread.start()



    def _run(self):
        while True:
            try:

                self.logger.info(
                    "Connexion WebSocket..."
                )

                self.ws = WebSocketApp(

                    self.ws_url,

                    on_open=self.on_open,

                    on_message=self.on_message,

                    on_close=self.on_close,

                    on_error=self.on_error

                )

                self.ws.run_forever()

            except Exception as e:

                self.logger.error(str(e))

            time.sleep(5)



    
    
    def on_open(self, ws):
        self.logger.info("WebSocket connecté.")

        registration = {
                "type": "register",
                "hostname": socket.gethostname(),
                "ip": get_local_ip(),
                "os": platform.system()
            }
        print(f"Registration : {registration}")
        ws.send(json.dumps(registration))



    def on_message(self, ws, message):
        try:
            message = json.loads(message)
            print(f"Message ws : {message}")

            message_type = message.get("type")

            if message_type == "registered":
                self.handle_registered(message)

            elif message_type == "command":
                self.handle_command(ws, message)

            else:
                self.logger.warning(
                    f"Type de message inconnu : {message_type}"
                )

        except Exception as e:
            self.logger.exception(e)




    def handle_registered(self, message):
        self.agent_id = message.get("agent_id")
        self.logger.info(f"Agent enregistré : {self.agent_id}")




    def handle_command(self, ws, command):

        action_name = command.get("action")
        action_id = command.get("action_id")
        parameters = command.get("params", {})

        if action_name not in self.actions:
            self.logger.warning(f"Action inconnue : {action_name}")
            return

        result = self.actions[action_name].execute(parameters)

        self.send_result(ws, action_id, action_name, result)


    def send_result(self, ws, action_id, action_name, result):
        response = {

            "type": "result",

            "action_id": action_id,

            "result": {
                "success": result.success,

                "action": action_name,

                "detail": (
                    result.message
                    if result.success
                    else result.error
                ),

                "machine": self.config.get(
                    "agent",
                    "name"
                ),

                "timestamp": datetime.now(UTC).isoformat()
            }
        }

        ws.send(json.dumps(response))



    def on_close(self, ws, code, reason):
        self.logger.warning("Connexion WebSocket fermée.")


    def on_error(self, ws, error):
        self.logger.error(error)






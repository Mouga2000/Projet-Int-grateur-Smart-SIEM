from communication import CommunicationClient
import requests
from config import Config
from logger import AgentLogger
from network.manager import NetworkManager

from actions.isolate_host import IsolateHostAction
from actions.disable_user import DisableUserAction
from actions.block_ip import BlockIPAction


class CommandService:

    def __init__(self):
        self.config = Config()
        self.client = CommunicationClient()

        #self.action_manager = action_manager
        self.logger = AgentLogger().get_logger()

        self.network = NetworkManager()

        self.disabled_actions = DisableUserAction()
        self.isolate_actions = IsolateHostAction()
        self.blocked_actions = BlockIPAction()


    def run(self):
        if not self.network.is_server_available():
            self.logger.warning("Serveur indisponible. Impossible de récupérer les actions.")
            return

        server = self.config.get("server")

        url_base = (
            f"{server['protocol']}://"
            f"{server['host']}:"
            f"{server['port']}"
        )

        self.get_blocked_actions(url_base)
        self.get_disabled_actions(url_base)
        self.get_isolate_actions(url_base)



    
    def get_blocked_actions(self, url_base):
        endpoint = self.config.get(
            "server",
            "api",
            "block_ip"
        )

        response = requests.get(url_base + endpoint, timeout=4)

        if response is None:
            return

        try:
            playbook = response.json()
        except Exception:
            self.logger.error("Réponse JSON invalide.")
            return

        if not playbook.get("enabled", True):
            return

        for step in playbook.get("steps", []):

            if step["action"] != "block_ip":
                continue

            self.blocked_actions.execute(step.get("params", {}))


        



    def get_disabled_actions(self, url_base):
        endpoint = self.config.get(
            "server",
            "api",
            "disable_user"
        )

        response = requests.get(url_base + endpoint, timeout=4)

        if response is None:
            return

        try:
            playbook = response.json()
        except Exception:
            self.logger.error("Réponse JSON invalide.")
            return

        if not playbook.get("enabled", True):
            return

        for step in playbook.get("steps", []):
            if step["action"] != "disable_user":
                continue

            self.disabled_actions.execute(step.get("params", {}))

            


    def get_isolate_actions(self, url_base):
        endpoint = self.config.get(
            "server",
            "api",
            "isolate_host"
        )

        response = requests.get(
            url_base + endpoint,
            timeout=4
        )

        if response is None:
            return

        try:
            playbook = response.json()
        except Exception:
            self.logger.error("Réponse JSON invalide.")
            return

        if not playbook.get("enabled", True):
            return

        for step in playbook.get("steps", []):
            if step["action"] != "isolate_host":
                continue

            self.isolate_actions.execute(
                step.get("params", {})
            )

        

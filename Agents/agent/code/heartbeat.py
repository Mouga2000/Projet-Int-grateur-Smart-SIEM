"""
Service d'envoi des Heartbeats.
"""

import time

import psutil

from code.config import Config
from code.communication import CommunicationClient
from code.logger import AgentLogger
from code.models.heartbeat import Heartbeat


class HeartbeatService:

    def __init__(self):

        self.config = Config()
        agent_logger = AgentLogger()
        self.logger = agent_logger.get_logger()
        self.client = CommunicationClient()



    def create_heartbeat(self) -> Heartbeat:
        """
        Construit le heartbeat à envoyer.
        """

        heartbeat = Heartbeat()

        heartbeat.agent_id = self.config.get("agent", "id")

        heartbeat.version = self.config.get("agent", "version")

        heartbeat.cpu = psutil.cpu_percent(interval=1)

        heartbeat.memory = psutil.virtual_memory().percent

        heartbeat.uptime = int(time.time() - psutil.boot_time())

        return heartbeat



    def send(self):

        heartbeat = self.create_heartbeat()
        endpoint = self.config.get("server", "api", "heartbeat")

        success = self.client.post(
            endpoint,
            heartbeat.to_dict()
        )

        if success:
            self.logger.info("Heartbeat envoyé.")

        else:
            self.logger.error("Impossible d'envoyer le heartbeat.")




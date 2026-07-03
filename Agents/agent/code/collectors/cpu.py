"""
Collecteur d'utilisation du processeur.
"""

import psutil

from code.config import Config
from code.logger import AgentLogger
from code.models.event import Event


class CPUCollector:

    def __init__(self):
        self.config = Config()
        log = AgentLogger()
        self.logger = log.get_logger()




    def collect(self) -> list[Event]:
        """ Collecte les informations CPU."""

        cpu_usage = psutil.cpu_percent(interval=1)

        event = Event()

        event.agent_id = self.config.get("agent", "id")

        event.collector = "CPUCollector"

        event.event_type = "cpu_usage"

        event.message = f"CPU Usage : {cpu_usage}%"

        event.data = {
            "usage": cpu_usage,

            "physical_cores": psutil.cpu_count(logical=False),

            "logical_cores": psutil.cpu_count(logical=True),

            "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else None
        }

        self.logger.info(f"CPU : {cpu_usage}%")

        return [event]




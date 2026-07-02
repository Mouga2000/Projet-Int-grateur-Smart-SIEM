

"""
Point d'entrée du Smart Agent.
"""

import signal
import sys
import time

from config import Config
from logger import AgentLogger
from scheduler import Scheduler, ScheduledTask
from heartbeat import HeartbeatService
from collectors.logs import LogsCollector
from communication import CommunicationClient
from collectors.cpu import CPUCollector
from collectors.memory import MemoryCollector
from collectors.process import ProcessCollector
from collectors.network import NetworkCollector
from collectors.services import ServicesCollector
from collectors.filesystem import FilesystemCollector

from communication_serveur import CommandService
from collectors.manager import CollectorManager

from storage.migrations import MigrationManager

from synchronisation.manager import TransferManager




MigrationManager().migrate()

log =  AgentLogger()
logger = log.get_logger()





class SmartAgent:

    def __init__(self):
        logger.info("Initialisation du Smart Agent...")

        self.scheduler = Scheduler()
        self.client = CommunicationClient()
        self.heartbeat = HeartbeatService()
        self.logs_collector = LogsCollector()
        self.collector_manager = CollectorManager(
            self.scheduler,
            self.client
        )

        self.transfer_manager = TransferManager()

        self.command_service = CommandService()
        
        self.configure_tasks()



    def configure_tasks(self):
        """
        Enregistre toutes les tâches périodiques.
        """

        self.collector_manager.register(
            "CPU",
            CPUCollector(),
            10

        )

        self.collector_manager.register(
            "Memory",
            MemoryCollector(),
            10

        )

        self.collector_manager.register(
            "Logs",
            LogsCollector(),
            5

        )

        self.collector_manager.register(
            "Network",
            NetworkCollector(),
            30

        )

        self.collector_manager.register(
            "Services",
            ServicesCollector(),
            60

        )

        self.collector_manager.register(
            "Filesystem",
            FilesystemCollector(),
            60
        )

        interval = Config().get(
            "sync",
            "interval"
        )
        self.scheduler.register(
            ScheduledTask(
                name="Transfer",
                interval=interval,
                callback=self.transfer_manager.run
            )
        )

        self.scheduler.register(
            ScheduledTask(
                name="Commands",
                interval=5,
                callback=self.command_service.run
            )
        )
        


    def start(self):
        logger.info("Démarrage du Smart Agent...")
        self.scheduler.start()


    def stop(self):
        logger.info("Arrêt du Smart Agent...")
        self.scheduler.stop()



def shutdown(agent):
    logger.info("Signal d'arrêt reçu.")
    agent.stop()
    sys.exit(0)






if __name__ == "__main__":
    agent = SmartAgent()

    signal.signal(
        signal.SIGINT,
        lambda s, f: shutdown(agent)
    )

    signal.signal(
        signal.SIGTERM,
        lambda s, f: shutdown(agent)
    )

    agent.start()

    while True:
        time.sleep(1)


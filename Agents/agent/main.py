

"""
Point d'entrée du Smart Agent.
"""

import signal
import time

import sys
from pathlib import Path

# Si le programme est figé (.exe), la racine est sys._MEIPASS
if getattr(sys, 'frozen', False):
    sys.path.insert(0, sys._MEIPASS)



from code.config import Config
from code.logger import AgentLogger
from code.scheduler import Scheduler, ScheduledTask
from code.heartbeat import HeartbeatService
from code.collectors.logs import LogsCollector
from code.collectors.cpu import CPUCollector
from code.collectors.memory import MemoryCollector
from code.collectors.process import ProcessCollector
from code.collectors.network import NetworkCollector
from code.collectors.services import ServicesCollector
from code.collectors.filesystem import FilesystemCollector

from code.communication_serveur import CommandService
from code.collectors.manager import CollectorManager

from code.storage.migrations import MigrationManager

from code.synchronisation.manager import TransferManager


MigrationManager().migrate()

log =  AgentLogger()
logger = log.get_logger()





class SmartAgent:

    def __init__(self):
        logger.info("Initialisation du Smart Agent...")

        self.scheduler = Scheduler()
        self.heartbeat = HeartbeatService()
        self.logs_collector = LogsCollector()
        self.collector_manager = CollectorManager(self.scheduler)

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
        """
        self.scheduler.register(
            ScheduledTask(
                name="Commands",
                interval=5,
                callback=self.command_service.run
            )
        )
        """
        


    def start(self):
        logger.info("Démarrage du Smart Agent...")
        self.command_service.start()
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


"""from config import Config

config = Config()

print(config.get("agent", "id"))

print(config.get("server", "host"))

print(config.get("heartbeat", "interval"))
"""


"""
from logger import AgentLogger

logger = AgentLogger().get_logger()

logger.debug("DEBUG")

logger.info("INFO")

logger.warning("WARNING")

logger.error("ERROR")

logger.critical("CRITICAL")
"""

"""
from models.event import Event

from communication import CommunicationClient

event = Event()

event.agent_id = "AGENT-002"

event.collector = "Logs"

event.event_type = "login"

event.message = "Utilisateur connecté"

client = CommunicationClient()

client.post(

    "/api/events",

    event.to_dict()

)
"""

"""
from scheduler import Scheduler, ScheduledTask
from heartbeat import HeartbeatService

heartbeat = HeartbeatService()
scheduler = Scheduler()
scheduler.register(
    ScheduledTask(

        "Heartbeat",
        30,
        heartbeat.send

    )
)
"""



"""

from scheduler import Scheduler, ScheduledTask


def hello():

    print("Hello")


scheduler = Scheduler()

scheduler.register(

    ScheduledTask(
        "HelloTask",

        5,

        hello
    )
)

scheduler.start()

while True:
    pass
"""

"""
from collectors.logs import LogsCollector

collector = LogsCollector()

events = collector.collect()

for event in events:
    print("="*50)

    client.post(
        "/api/events",

        event.to_dict()

    )
"""

"""
Point d'entrée du Smart Agent.

Auteur : Nehemie Mouga
"""

import signal
import sys
import time

from logger import AgentLogger
from scheduler import Scheduler, ScheduledTask
from heartbeat import HeartbeatService
from collectors.logs import LogsCollector
from communication import CommunicationClient
from collectors.cpu import CPUCollector



log =  AgentLogger()
logger = log.get_logger()


class SmartAgent:

    def __init__(self):
        logger.info("Initialisation du Smart Agent...")

        self.scheduler = Scheduler()
        self.client = CommunicationClient()
        self.heartbeat = HeartbeatService()
        self.logs_collector = LogsCollector()
        self.configure_tasks()
        self.cpu_collector = CPUCollector()



    def configure_tasks(self):
        """
        Enregistre toutes les tâches périodiques.
        """

        self.scheduler.register(
            ScheduledTask(
                name="Heartbeat",

                interval=30,
                callback=self.heartbeat.send
            )
        )

        self.scheduler.register(
            ScheduledTask(
                name="LogsCollector",

                interval=5,
                callback=self.collect_logs
            )
        )

        self.scheduler.register(
            ScheduledTask(
                name="CPUCollector",

                interval=10,
                callback=self.collect_cpu
            )
        )



    def collect_logs(self):
        """Collecte puis envoie les événements."""
        events = self.logs_collector.collect()

        for event in events:
            self.client.post(
                #"/api/events",
                "/api/v1/logs/ingest",
                event.to_dict()
            )
            print("="*50)
            print(event.to_dict())


    def collect_cpu(self):
        events = self.cpu_collector.collect()
        
        for event in events:
            self.client.post(

                #"/api/events",
                "/api/v1/logs/ingest",
                event.to_dict()
            )
            print("="*50)
            print(event.to_dict())



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


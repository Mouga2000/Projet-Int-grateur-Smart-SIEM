"""
Collecteur des processus.

Auteur : Nehemie Mouga
"""

import psutil

from code.config import Config
from code.logger import AgentLogger
from code.models.event import Event


class ProcessCollector:

    def __init__(self):
        self.config = Config()

        log = AgentLogger()
        self.logger = log.get_logger()



    def collect(self) -> list[Event]:

        events = []

        limit = self.config.get(
            "process",
            "top_processes"
        )

        processes = []

        for proc in psutil.process_iter(
            [
                "pid",
                "name",
                "username",
                "cpu_percent",
                "memory_percent"
            ]
        ):

            try:
                processes.append(proc.info)

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied
            ):
                continue

        processes.sort(
            key=lambda p: p["cpu_percent"],
            reverse=True
        )

        for proc in processes[:limit]:
            event = Event()

            event.agent_id = self.config.get(
                "agent",
                "id"
            )

            event.collector = "ProcessCollector"

            event.event_type = "process_snapshot"

            event.message = (
                f"Process {proc['name']} "
                f"(PID {proc['pid']})"
            )

            event.data = {
                "pid": proc["pid"],

                "name": proc["name"],

                "user": proc["username"],

                "cpu_percent": proc["cpu_percent"],

                "memory_percent": round(
                    proc["memory_percent"], 2
                )
            }

            events.append(event)

        self.logger.info(f"{len(events)} processus collectés")

        return events



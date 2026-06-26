"""
Collecteur des systèmes de fichiers.
"""

import psutil

from config import Config
from logger import AgentLogger
from models.event import Event


class FilesystemCollector:

    def __init__(self):
        self.config = Config()
        self.logger = AgentLogger().get_logger()



    def collect(self):
        events = []

        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(
                    partition.mountpoint
                )

            except PermissionError:
                continue

            event = Event()

            event.agent_id = self.config.get("agent", "id")

            event.collector = "FilesystemCollector"

            event.event_type = "disk_usage"

            event.message = (
                f"{partition.device} "
                f"{usage.percent}% utilisé"
            )

            event.data = {

                "device": partition.device,

                "mountpoint": partition.mountpoint,

                "filesystem": partition.fstype,

                "total_gb": round(
                    usage.total / (1024**3),
                    2
                ),

                "used_gb": round(
                    usage.used / (1024**3),
                    2
                ),

                "free_gb": round(
                    usage.free / (1024**3),
                    2
                ),

                "usage_percent": usage.percent

            }

            events.append(event)

        self.logger.info(
            f"{len(events)} partitions collectées"
        )

        return events





"""
Collecteur mémoire.
"""

import psutil

from code.config import Config
from code.logger import AgentLogger
from code.models.event import Event


class MemoryCollector:

    def __init__(self):
        self.config = Config()

        log = AgentLogger()
        self.logger = log.get_logger()


    def collect(self) -> list[Event]:

        memory = psutil.virtual_memory()

        swap = psutil.swap_memory()

        event = Event()

        event.agent_id = self.config.get("agent", "id")

        event.collector = "MemoryCollector"

        event.event_type = "memory_usage"

        event.message = (
            f"RAM Usage : {memory.percent}%"
        )

        event.data = {

            "usage_percent": memory.percent,

            "total_MB": round(memory.total / (1024 * 1024), 2),

            "available_MB": round(memory.available / (1024 * 1024), 2),

            "used_MB": round(memory.used / (1024 * 1024), 2),

            "free_MB": round(memory.free / (1024 * 1024), 2),

            "swap_used_MB": round(
                swap.used / (1024 * 1024), 2
            ),

            "swap_percent": swap.percent

        }

        self.logger.info(f"RAM : {memory.percent}%")

        return [event]

        
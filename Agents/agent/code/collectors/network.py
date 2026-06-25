"""
Collecteur réseau.

Auteur : Nehemie Mouga
"""

import socket
import psutil

from config import Config
from logger import AgentLogger
from models.event import Event


class NetworkCollector:

    def __init__(self):
        self.config = Config()
        log = AgentLogger()
        self.logger = log.get_logger()



    def collect(self) -> list[Event]:
        events = []

        max_connections = self.config.get(
            "network",
            "max_connections"
        )

        connections = psutil.net_connections()

        for conn in connections[:max_connections]:

            try:
                local_ip = conn.laddr.ip if conn.laddr else None
                local_port = conn.laddr.port if conn.laddr else None

                remote_ip = conn.raddr.ip if conn.raddr else None
                remote_port = conn.raddr.port if conn.raddr else None

                event = Event()

                event.agent_id = self.config.get(
                    "agent",
                    "id"
                )

                event.collector = "NetworkCollector"

                event.event_type = "network_connection"

                event.message = (
                    f"{local_ip}:{local_port} -> "
                    f"{remote_ip}:{remote_port}"
                )

                event.data = {

                    "family": str(conn.family),

                    "type": str(conn.type),

                    "status": conn.status,

                    "pid": conn.pid,

                    "local_ip": local_ip,

                    "local_port": local_port,

                    "remote_ip": remote_ip,

                    "remote_port": remote_port

                }

                events.append(event)

            except Exception:
                continue

        self.logger.info(f"{len(events)} connexions réseau collectées")

        return events


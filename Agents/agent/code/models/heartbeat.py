"""
Heartbeat envoyé périodiquement au serveur.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import socket
import platform


@dataclass
class Heartbeat:

    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    agent_id: str = ""

    hostname: str = field(default_factory=socket.gethostname)

    operating_system: str = field(default_factory=platform.system)

    version: str = "1.0.0"

    status: str = "ONLINE"

    cpu: float = 0

    memory: float = 0

    uptime: int = 0


    def to_dict(self):
        return asdict(self)
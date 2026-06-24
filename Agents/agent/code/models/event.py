"""
Modèle représentant un événement envoyé au serveur SIEM.

"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, Any
import socket
import platform
import uuid




def get_local_ip() -> str:
    try:
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connexion externe fictive
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return "127.0.0.1"


def get_mac_address() -> str:
    try:
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                       for elements in range(0, 2*6, 2)][::-1])
        return mac
    except Exception:
        return "00:00:00:00:00:00"



@dataclass
class Event:

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    agent_id: str = ""

    source_ip: str = field(default_factory=get_local_ip)

    mac_address: str = field(default_factory=get_mac_address)

    hostname: str = field(default_factory=socket.gethostname)

    operating_system: str = field(default_factory=platform.system)

    severity: str = "INFO"

    collector: str = ""

    event_type: str = ""

    message: str = ""

    data: Dict[str, Any] = field(default_factory=dict)



    def to_dict(self):
        return asdict(self)


    def to_json(self):
        import json

        return json.dumps(
            self.to_dict(),
            ensure_ascii=False
        )



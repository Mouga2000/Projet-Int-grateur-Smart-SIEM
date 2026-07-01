"""
Réponse provenant du serveur Smart SIEM.
"""

from dataclasses import dataclass


@dataclass
class ServerResponse:

    success: bool
    message: str
    command: str | None = None
    payload: dict | None = None




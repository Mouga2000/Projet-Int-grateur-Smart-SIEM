"""
Gestionnaire de la connectivité réseau.
"""

from communication import CommunicationClient


class NetworkManager:

    def __init__(self):
        self.client = CommunicationClient()

    def is_server_available(self):
        try:
            response = self.client.ping()
            return response

        except Exception:
            return False



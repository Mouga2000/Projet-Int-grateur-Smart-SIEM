"""
Gestionnaire de la file d'attente.
"""

from network.manager import NetworkManager

from storage.repositories.event_repository import EventRepository

from communication import CommunicationClient
from logger import AgentLogger


class QueueManager:

    def __init__(self):
        self.network = NetworkManager()
        self.repository = EventRepository()
        self.client = CommunicationClient()
        
        self.logs = AgentLogger().get_logger()


    def publish(self, event):
        if self.network.is_server_available():
            success = self.client.post(event.to_dict())

            if success:
                return True
        self.logs.info ("Reseau indisponible, impossible de joindre le serveur SIEM")
        self.repository.save(event)
        return 
        






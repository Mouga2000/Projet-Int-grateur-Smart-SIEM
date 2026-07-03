"""
Synchronisation des événements.
"""

import json

from code.logger import AgentLogger
from code.network.manager import NetworkManager
from code.storage.repositories.batch.batch_manager import BatchManager
from code.communication import CommunicationClient
from code.storage.repositories.event_repository import EventRepository


class EventSync:

    def __init__(self):
        self.logger = AgentLogger().get_logger()

        self.network = NetworkManager()
        self.batch_manager = BatchManager()
        self.client = CommunicationClient()
        self.event_repository = EventRepository()


    def run(self):
        
        if not self.network.is_server_available():
            self.logger.info("Serveur indisponible.")
            return

        batch = self.batch_manager.next_batch()

        if len(batch) == 0:
            return

        self.logger.info(f"{len(batch)} événements en attente de synchronisation.")
        
        ids = [row["id"] for row in batch]                  # récupération des IDs

        self.event_repository.mark_sending(ids)              # verrouillage des événements

        success_ids = []
        failed_ids = []

        for row in batch:
            try:
                payload = json.loads(row["payload"])
                success = self.client.post(payload)

                if success:
                    success_ids.append(row["id"])
                else:
                    failed_ids.append(row["id"])

            except Exception as e:

                self.logger.error(e)
                failed_ids.append(row["id"])

        # Mise à jour de la base
        if success_ids:
            self.event_repository.mark_sent(success_ids)

            self.logger.info(f"{len(success_ids)} événements synchronisés.")

        if failed_ids:
            self.event_repository.increment_retry(failed_ids)

            self.logger.warning(f"{len(failed_ids)} événements non synchronisés.")

       
        self.event_repository.delete_sent()              # nettoyage des événements envoyés



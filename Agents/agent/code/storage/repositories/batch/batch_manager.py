"""
Gestionnaire des lots d'événements.
"""

from code.config import Config
from code.storage.repositories.event_repository import EventRepository


class BatchManager:
    def __init__(self):
        self.config = Config()
        self.repository = EventRepository()


    def next_batch(self):
        batch_size = self.config.get(
            "sync",
            "batch_size"
        )

        events = self.repository.get_pending(
            limit=batch_size
        )
        print("Nombre d'événements :", len(events))

        for event in events[:3]:
            print(dict(event))

        return events



    def has_pending(self):
        return self.repository.count_pending() > 0



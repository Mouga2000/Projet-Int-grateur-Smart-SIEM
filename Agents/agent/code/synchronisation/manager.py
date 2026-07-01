"""
Gestionnaire des transferts.
"""

from synchronisation.events_syndro import EventSync


class TransferManager:
    def __init__(self):
        self.event_sync = EventSync()


    def run(self):
        self.event_sync.run()





"""
Gestionnaire des collecteurs.
"""

from scheduler import ScheduledTask
from storage.repositories.manager import QueueManager


class CollectorManager:

    def __init__(self, scheduler, client):
        self.scheduler = scheduler
        self.client = client
        self.collectors = []
        self.queue = QueueManager()


    def register( self, name, collector, interval):

        self.collectors.append(collector)

        self.scheduler.register(
            ScheduledTask(
                name=name,

                interval=interval,
                callback=lambda c=collector:self.execute(c)

            )

        )

    def execute(self, collector):
        events = collector.collect()

        for event in events:
            self.queue.publish(event)



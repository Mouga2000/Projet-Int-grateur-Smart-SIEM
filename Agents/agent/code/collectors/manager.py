
"""
Gestionnaire des collecteurs.
"""

from code.scheduler import ScheduledTask
from code.storage.repositories.manager import QueueManager


class CollectorManager:

    def __init__(self, scheduler):
        self.scheduler = scheduler
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



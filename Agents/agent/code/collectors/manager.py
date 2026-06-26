
"""
Gestionnaire des collecteurs.
"""

from scheduler import ScheduledTask


class CollectorManager:

    def __init__(self, scheduler, client):
        self.scheduler = scheduler
        self.client = client
        self.collectors = []
        self.url_event = "/api/events"


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

            self.client.post(
                self.url_event,
                event.to_dict()
            )



"""
Planificateur principal.
"""
import threading
import time
from code.logger import AgentLogger



class Scheduler:

    def __init__(self):

        log= AgentLogger()
        self.logger = log.get_logger()

        self.tasks = []


    def register(self, task):

        self.tasks.append(task)
        self.logger.info(f"Tâche enregistrée : {task.name}")



    def start(self):
        self.logger.info("Démarrage du scheduler...")

        for task in self.tasks:

            task.start()

        self.logger.info("Scheduler démarré.")


    def stop(self):
        self.logger.info("Arrêt du scheduler...")

        for task in self.tasks:

            task.stop()

        self.logger.info("Scheduler arrêté.")





class ScheduledTask:
    """
    Représente une tâche périodique.
    """

    def __init__(self, name, interval, callback):

        self.name = name
        self.interval = interval
        self.callback = callback
        self.thread = None
        self.stop_event = threading.Event()


    def start(self):

        self.thread = threading.Thread(
            target=self.run,
            daemon=True
        )

        self.thread.start()


    def stop(self):
        self.stop_event.set()


    def run(self):
        log= AgentLogger()
        logger = log.get_logger()

        logger.info("Task started.")

        while not self.stop_event.is_set():

            try:
                self.callback()

            except Exception as e:
                logger.exception(e)

            self.stop_event.wait(self.interval)

        logger.info("Task stopped.")



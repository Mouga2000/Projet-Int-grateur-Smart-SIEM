"""
Collecteur des journaux système.

Auteur : Nehemie Mouga
"""

import os
import platform

from code.models.event import Event
from code.config import Config
from code.logger import AgentLogger


class LogsCollector:

    def __init__(self):
        self.config = Config()

        log = AgentLogger()
        self.logger = log.get_logger()

        self.positions = {}


    #Retourne la liste des fichiers de logs en fonction du système d'exploitation.
    def get_log_files(self) -> list[str]:
        
        system = platform.system()

        if system == "Linux":
            return self.config.get(
                "logs",
                "paths",
                "linux"
            )

        elif system == "Windows":

            return self.config.get(
                "logs",
                "paths",
                "windows"
            )

        return []



    def read_new_lines(self, filepath: str) -> list[Event]:
        events = []

        if not os.path.exists(filepath):
            self.logger.warning(
                f"Fichier introuvable : {filepath}"
            )

            return events

        # Premier lancement
        if filepath not in self.positions:
            if self.config.get("logs", "read_from_end"):
                self.positions[filepath] = os.path.getsize(filepath)
            else:
                self.positions[filepath] = 0


        with open(filepath, "r", encoding="utf-8", errors="ignore" ) as file:
            file.seek(self.positions[filepath])

            for line in file:
                line = line.strip()

                if not line:
                    continue

                event = Event()

                event.agent_id = self.config.get("agent", "id")

                event.collector = "LogsCollector"

                event.event_type = "system_log"

                event.message = line

                event.data = {"file": filepath}

                events.append(event)

            self.positions[filepath] = file.tell()

        return events



    def collect(self) -> list[Event]:
        """ Collecte les nouveaux logs. """
        events = []

        for logfile in self.get_log_files():
            events.extend(
                self.read_new_lines(logfile)
            )

        self.logger.info(f"{len(events)} nouveaux événements collectés.")

        return events



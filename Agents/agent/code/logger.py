import logging
import os
from logging.handlers import RotatingFileHandler
import socket

from code.config import Config


class AgentLogger:

    def __init__(self):

        self.config = Config()
        hostname = socket.gethostname()
        self.logger = logging.getLogger(f"Agent.{hostname}")

        self.logger.setLevel(self.config.get("logging", "level"))
        self.logger.propagate = False

       
        if self.logger.handlers:
            return

        self.__create_log_directory()

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s"
        )

        file_handler = RotatingFileHandler(
            filename=self.config.get("logging", "file"),
            maxBytes=self.config.get("logging", "max_size"),
            backupCount=self.config.get("logging", "backup_count"),
            encoding="utf-8"
        )

        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        if self.config.get("logging", "console"):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)

            self.logger.addHandler(console_handler)



    def __create_log_directory(self):

        logfile = self.config.get("logging", "file")
        folder = os.path.dirname(logfile)
        os.makedirs(folder, exist_ok=True)



    def get_logger(self):
        return self.logger






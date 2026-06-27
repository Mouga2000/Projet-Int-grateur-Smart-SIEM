"""
Gestionnaire de la base SQLite.
"""

from pathlib import Path
import sqlite3


class Database:

    def __init__(self):
        root = Path(__file__).resolve().parent
        self.database_path = (
            root /
            "data" /
            "smart_agent.db"
        )

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.connection = None

    def connect(self):

        if self.connection is None:

            self.connection = sqlite3.connect(
                self.database_path,
                check_same_thread=False
            )

            self.connection.row_factory = sqlite3.Row

        return self.connection


    def cursor(self):
        return self.connect().cursor()


    def commit(self):
        self.connect().commit()


    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None




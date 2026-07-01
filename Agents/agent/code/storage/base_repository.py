"""
Classe mère de tous les repositories.
"""

from abc import ABC

from storage.database import Database


class BaseRepository(ABC):

    def __init__(self):
        self.database = Database()
        self.connection = self.database.connect()

        self.cursor = self.connection.cursor()

    

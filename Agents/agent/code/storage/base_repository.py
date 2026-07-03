"""
Classe mère de tous les repositories.
"""

from abc import ABC

from code.storage.database import Database


class BaseRepository(ABC):

    def __init__(self):
        self.database = Database()
        self.connection = self.database.connect()


    

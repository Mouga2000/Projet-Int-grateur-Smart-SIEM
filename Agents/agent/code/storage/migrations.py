"""
Gestionnaire des migrations SQLite.
"""

from storage.database import Database
from logger import AgentLogger




class MigrationManager:

    CURRENT_VERSION = 1

    def __init__(self):
        self.database = Database()
        log = AgentLogger()
        self.logs = log.get_logger()
        self.connection = self.database.connect()
        self.cursor = self.connection.cursor()



    def migrate(self):
        
        self.create_version_table()
        version = self.get_version()

        if version < 1:
            self.logs.info(f"Migration manquante")
            self.logs.info(f"Initialisation de la migration ...")
            self.create_events_table()
            self.set_version(1)
        else:
            self.logs.info(f"Migration existante")


    def create_version_table(self):
        try:

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_version(
                    version INTEGER NOT NULL
                )
            """)

            self.connection.commit()
            self.cursor.execute(
                "SELECT COUNT(*) FROM schema_version"
            )

            count = self.cursor.fetchone()[0]

            if count == 0:
                self.cursor.execute(
                    "INSERT INTO schema_version(version) VALUES (0)"
                )
                self.connection.commit()
            
        except Exception as e:
            self.logs.error(f"Erreur de création de la bd : {e}")




    def get_version(self):
        self.cursor.execute(
            "SELECT version FROM schema_version"
        )
        return self.cursor.fetchone()[0]




    def set_version(self, version):
        self.cursor.execute(
            "UPDATE schema_version SET version=?",
            (version,)
        )
        self.connection.commit()



    def create_events_table(self):

        try:

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS events(

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    collector TEXT NOT NULL,

                    event_type TEXT NOT NULL,

                    priority INTEGER DEFAULT 1,

                    status TEXT DEFAULT 'PENDING',

                    retry_count INTEGER DEFAULT 0,

                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    payload TEXT NOT NULL,

                    sync_attempts INTEGER DEFAULT 0,

                    last_sync_at TIMESTAMP NULL
                )

            """)

            self.connection.commit()

            

        except Exception as e:
            self.logs.error(f"Erreur de migration des tables : {e}")







import json
from storage.base_repository import BaseRepository


class EventRepository(BaseRepository):

    def save(self, event):
        payload_json = json.dumps(event.data if hasattr(event, 'data') else event, ensure_ascii=False)
        collector_str = str(event.collector)
        event_type_str = str(event.event_type)

        self.cursor.execute(
            """ INSERT INTO events(collector, event_type, payload ) VALUES(?, ?, ?) """,
            (
                collector_str, event_type_str, payload_json
            )

        )

        self.connection.commit()

        return self.cursor.lastrowid


    
    def get_pending(self, limit=100):

        self.cursor.execute(
            """
                SELECT *

                FROM events

                WHERE status='PENDING'

                ORDER BY id

                LIMIT ?

            """,

            (limit,)
        )

        return self.cursor.fetchall()



    def mark_sent(self, ids ):
        placeholders = ",".join( "?" for _ in ids )

        self.cursor.execute(
            f"""
                UPDATE events
                SET status='SENT'
                WHERE id IN ({placeholders})
            """,
            ids
        )

        self.connection.commit()



    def delete_sent(self):
        self.cursor.execute(""" DELETE FROM events WHERE status='SENT' """ )
        self.connection.commit()






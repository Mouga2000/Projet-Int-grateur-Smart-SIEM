import json
from storage.base_repository import BaseRepository


class EventRepository(BaseRepository):

    def save(self, event):
        payload_json = json.dumps(event.to_dict(), ensure_ascii=False)
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
        self.cursor.executemany(
            """
                UPDATE events
                SET status='SENT'
                WHERE id = ?
            """,
            [(event_id,) for event_id in ids]
        )

        self.connection.commit()



    def count_pending(self):
        self.cursor.execute("""
                SELECT COUNT (*)
                FROM events
                WHERE status = 'PENDING'
            """)
        value = self.cursor.fetchone()[0]
        return value

    

    def reset_sending(self):
        self.cursor.execute("""
            UPDATE events
            SET status = 'PENDING'
            WHERE status = 'SENDING'
            """)
        self.connection.commit()


    
    def mark_sending(self, ids):
        self.cursor.executemany(
            """
            UPDATE events
            SET status = 'SENDING'
            WHERE id=?
            """, [(event_id,) for event_id in ids]
        )
        self.connection.commit()



    def delete_sent(self):
        self.cursor.execute(""" DELETE FROM events WHERE status='SENT' """ )
        self.connection.commit()


    def increment_retry(self, ids):
        self.cursor.executemany(
        """
            UPDATE events
            SET retry_count = retry_count + 1,
                status='FAILED'
            WHERE id=?
        """,
        [(event_id,) for event_id in ids]
        )
        self.connection.commit()

    
    def mark_failed(self, ids):
        self.cursor.executemany(
            """
            UPDATE events
            SET status='FAILED'
            WHERE id=?
            """,
            [(event_id,) for event_id in ids]
        )
        self.connection.commit()






import json
import threading 
from code.storage.base_repository import BaseRepository


db_lock = threading.Lock()

class EventRepository(BaseRepository):

    def save(self, event):
        payload_json = json.dumps(event.to_dict(), ensure_ascii=False)
        collector_str = str(event.collector)
        event_type_str = str(event.event_type)

        with db_lock:
            cursor = self.connection.cursor()
            try:
                cursor.execute(
                    """ INSERT INTO events(collector, event_type, payload ) VALUES(?, ?, ?) """,
                    (collector_str, event_type_str, payload_json)
                )
                self.connection.commit()
                return cursor.lastrowid
            finally:
                cursor.close()



    def get_pending(self, limit=100):
        with db_lock:
            cursor = self.connection.cursor()
            try:
                cursor.execute(
                    """
                        SELECT *
                        FROM events
                        WHERE status='PENDING'
                        ORDER BY id
                        LIMIT ?
                    """,
                    (limit,)
                )
                return cursor.fetchall()
            finally:
                cursor.close()




    def mark_sent(self, ids):
        with db_lock:
            cursor = self.connection.cursor()
            try:
                cursor.executemany(
                    """
                        UPDATE events
                        SET status='SENT'
                        WHERE id = ?
                    """,
                    [(event_id,) for event_id in ids]
                )
                self.connection.commit()
            finally:
                cursor.close()



    def count_pending(self):
        with db_lock:
            cursor = self.connection.cursor()
            try:
                cursor.execute("""
                        SELECT COUNT (*)
                        FROM events
                        WHERE status = 'PENDING'
                    """)
                value = cursor.fetchone()[0] 
                return value
            finally:
                cursor.close()



    def reset_sending(self):
        with db_lock:
            cursor = self.connection.cursor()
            try:
                cursor.execute("""
                    UPDATE events
                    SET status = 'PENDING'
                    WHERE status = 'SENDING'
                    """)
                self.connection.commit()
            finally:
                cursor.close()




    def mark_sending(self, ids):
        with db_lock:
            cursor = self.connection.cursor()
            try:
                cursor.executemany(
                    """
                    UPDATE events
                    SET status = 'SENDING'
                    WHERE id=?
                    """, [(event_id,) for event_id in ids]
                )
                self.connection.commit()
            finally:
                cursor.close()


    def delete_sent(self):
        with db_lock:
            cursor = self.connection.cursor()
            try:
                cursor.execute(""" DELETE FROM events WHERE status='SENT' """)
                self.connection.commit()
            finally:
                cursor.close()



    def increment_retry(self, ids):
        with db_lock:
            cursor = self.connection.cursor()
            try:
                cursor.executemany(
                """
                    UPDATE events
                    SET retry_count = retry_count + 1,
                        status='FAILED'
                    WHERE id=?
                """,
                [(event_id,) for event_id in ids]
                )
                self.connection.commit()
            finally:
                cursor.close()



    def mark_failed(self, ids):
        with db_lock:
            cursor = self.connection.cursor()
            try:
                cursor.executemany(
                    """
                    UPDATE events
                    SET status='FAILED'
                    WHERE id=?
                    """,
                    [(event_id,) for event_id in ids]
                )
                self.connection.commit()
            finally:
                cursor.close()



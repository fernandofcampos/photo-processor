import psycopg2
from psycopg2.extras import RealDictCursor


class DB:
    def __init__(self, params):
        self.conn = psycopg2.connect(params)

    def close(self):
        self.conn.close()

    def get_photos_by_status(self, status):
        try:
            cur = self.conn.cursor(cursor_factory=RealDictCursor)
            q = 'SELECT * from photos WHERE status = %s'
            cur.execute(q, (status,))
            return cur.fetchall()
        finally:
            if cur:
                cur.close()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

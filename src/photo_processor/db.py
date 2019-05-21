import psycopg2
from psycopg2.extras import RealDictCursor


class DB:
    def __init__(self, params):
        self.conn = psycopg2.connect(params)

    def close(self):
        self.conn.close()

    def get_photo(self, uuid):
        try:
            cur = self.conn.cursor(cursor_factory=RealDictCursor)
            q = 'SELECT * from photos WHERE uuid = %s'
            cur.execute(q, (uuid,))
            return cur.fetchone()
        finally:
            if cur:
                cur.close()

    def get_photos_by_status(self, status):
        try:
            cur = self.conn.cursor(cursor_factory=RealDictCursor)
            q = 'SELECT * from photos WHERE status = %s'
            cur.execute(q, (status,))
            return cur.fetchall()
        finally:
            if cur:
                cur.close()

    def update_photo_status(self, uuid, status):
        try:
            cur = self.conn.cursor()
            q = 'UPDATE photos SET status = %s WHERE uuid = %s'
            cur.execute(q, (status, uuid))
            return cur.rowcount
        finally:
            if cur:
                cur.close()

    def insert_photo_thumbnail(self, uuid, width, height, file):
        try:
            cur = self.conn.cursor()
            q = ''' INSERT INTO photo_thumbnails(photo_uuid, width,
                    height, url) VALUES (%s, %s, %s, %s) '''
            cur.execute(q, (uuid, width, height, file))
            return cur.rowcount
        finally:
            if cur:
                cur.close()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

import sqlite3
from sqlite3 import Error
import time


#("o2", name, url, )


class DBConn(object):
    def __init__(self, db_file='downloads.sqlite'):
        self.schema = """
            CREATE TABLE
            IF NOT EXISTS downloads (
                id integer PRIMARY KEY,
                site text NOT NULL,
                name text NOT NULL,
                uri text,
                timestamp integer
            );
            """
        self.conn = self.create_connection(db_file)
        if self.conn is not None:
            self.create_table(self.conn, self.schema)
        else:
            print("failed to create a database")

    def bye(self):
        self.conn.close()
        return

    def add_download(self, site, name, uri):
        timestamp = int(time.time())
        data = (site, name, uri, timestamp)
        statement = """
            INSERT INTO downloads(site, name, uri, timestamp) VALUES (?, ?, ?, ?);
        """
        cur = self.conn.cursor()
        cur.execute(statement, data)
        return cur.lastrowid

    def has_entry(self, site, name):
        statement = """
            SELECT id FROM downloads WHERE site = ? and name = ?;
            """
        cur = self.conn.cursor()
        cur.execute(statement, (site, name))
        rows = cur.fetchall()
        if len(rows) > 0:
            return True
        else:
            return False

    def create_connection(self, db_file):
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
            conn.close()

    def create_table(self, conn, schema):
        try:
            c = conn.cursor()
            c.execute(schema)
        except Exception:
            print("failed to execute schema")
            raise


if __name__ == '__main__':
    db = DBConn()
    db.add_download(site="test", name="testname", uri="random")
    assert db.check_download(site="test2", name="bla") is False
    assert db.check_download(site="test", name="testname") is True
    db.bye()

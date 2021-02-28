import sqlite3
from sqlite3 import Error
import os

class Storage(object):
    """docstring for Storage."""
    connection = None

    def __init__(self):
        conn = None
        try:
            file_location = os.path.dirname(os.path.realpath(__file__))
            self.connection = sqlite3.connect(r"{}/database.db".format(file_location))
            self.connection.row_factory = sqlite3.Row
        except Error as e:
            print(e)

    def __del__(self):
        if self.connection:
            self.connection.close()

    def select_multiple(self, statement, parameters=[]):
        cursor = self.connection.cursor()
        cursor.execute(statement, parameters)
        return cursor.fetchall()

    def select_row(self, statement, parameters=[]):
        cursor = self.connection.cursor()
        cursor.execute(statement, parameters)
        return cursor.fetchone()

    def query(self, statement, parameters=[]):
        """ run a query from statement on the connection object
        :param statement: a sql statement
        :return:
        """
        try:
            c = self.connection.cursor()
            c.execute(statement, parameters)
            self.connection.commit()
        except Error as e:
            print(e)

    def setup(self):
        self.query("""CREATE TABLE IF NOT EXISTS messages (
  id integer PRIMARY KEY,
  process_name varchar(256),
  content text
);
""")
        self.query("""CREATE TABLE IF NOT EXISTS subscriptions (
id integer PRIMARY KEY,
process_name varchar(256),
server_id varchar(256) NULL,
channel_id varchar(256) NULL
)""")

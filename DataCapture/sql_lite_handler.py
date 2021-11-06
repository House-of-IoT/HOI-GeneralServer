import sqlite3
from queries import Queries

class SQLiteHandler:
    def __init__(self,db_path):
        try:
            self.connection = sqlite3.connect(db_path)
            self.cursor = self.connection.cursor()
            self.successful_connection = True
        except:
            self.successful_connection = False

    def create_tables_if_needed(self):
        self.cursor.execute(Queries.create_notification_table)
        self.cursor.execute(Queries.create_action_execution_history)
        self.cursor.execute(Queries.create_contacts_table)
        self.cursor.execute(Queries.create_banned_history)
        self.cursor.execute(Queries.create_connection_history)

    def insert_notification():
        pass

    def insert_action_execution():
        pass

    def insert_contact():
        pass

    def insert_banned_ip():
        pass

    def insert_connection():
        pass
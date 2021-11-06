import sqlite3
from queries import LiteQueries

class SQLiteHandler:
    def __init__(self,db_path,permanent_data_store = False):
        try:
            self.connection = sqlite3.connect(db_path)
            self.cursor = self.connection.cursor()
            self.successful_connection = True
        except:
            self.successful_connection = False

    def create_tables_if_needed(self):
        self.cursor.execute(LiteQueries.create_notification_table)
        self.cursor.execute(LiteQueries.create_action_execution_history)
        self.cursor.execute(LiteQueries.create_contacts_table)
        self.cursor.execute(LiteQueries.create_banned_history)
        self.cursor.execute(LiteQueries.create_connection_history)

 
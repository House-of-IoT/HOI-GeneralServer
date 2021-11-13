from datetime import datetime
import aiopg
from .queries import PostgresQueries
import os

"""
Handles the connection to the database and handles
query execution.
"""

class SQLHandler:
    def __init__(self):
        self.connected = False

    async def gather_connection(self):
        try:
            host = os.environ("hoi_db_host")
            port = os.environ("hoi_db_port")
            database = os.environ("hoi_db_name")
            user = os.environ("hoi_db_user")      
            password = os.environ("hoi_db_pw")

            self.connection = await aiopg.connect(
                database=database,
                user=user,
                port=port,
                password=password,
                host=host)

            self.connected = True

        except Exception as e:
            print(e)
            raise e

    async def create_tables_if_needed(self,cursor):
        await cursor.execute(PostgresQueries.create_notification_table)
        await cursor.execute(PostgresQueries.create_action_execution_history)
        await cursor.execute(PostgresQueries.create_contacts_table)
        await cursor.execute(PostgresQueries.create_banned_history)
        await cursor.execute(PostgresQueries.create_connection_history)

    async def remove_expired_rows(self,date,table_name,date_column_name,cursor):
        await cursor.execute(PostgresQueries.remove_expired_history_query(
            table_name,date_column_name,date))

    async def create_notification(self,name,desc,date,cursor):
        await cursor.execute(PostgresQueries.insert_notification_query(name,desc,date))

    async def create_action_execution(self,executor,action,bot_name,type_data,date,cursor):
        await cursor.execute(
            PostgresQueries.insert_action_execution_query(executor,action,bot_name,type_data,date))
    
    async def create_connection_history(self,name,type_data,date,cursor):
        await cursor.execute(PostgresQueries.insert_connection_query(name,type_data,date))

    async def create_banned(self,ip,cursor):
        await cursor.execute(PostgresQueries.insert_banned_query(ip))
        
    async def create_contact(self,name,number,cursor):
        await cursor.execute(PostgresQueries.insert_contact_query(name,number))

    async def get_all_rows(self,table_name,cursor):
        await cursor.execute(PostgresQueries.select_query(table_name))
        return await self.all_rows(cursor)
    
    async def all_rows(self,cursor):
        results = []
        async for row in cursor:
            results.append(row)
        return results
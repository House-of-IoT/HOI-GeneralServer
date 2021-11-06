import asyncio
import aiopg
import os

from queries import PostgresQueries

class SQLHandler:
    async def __init__(self,parent):
        try:
            await self.gather_connection()
            self.parent = parent
            self.successful_connection = True
        except:
            self.successful_connection = False

    async def gather_connection(self):
        host = os.environ.get("db_h"),
        port = os.environ.get("db_p")
        database = os.environ.get("HOI")
        user = os.environ.get("HOI_USER")        
        password = os.environ.get("HOI_PW")
        pool = await aiopg.create_pool(f""" 
            dbname={database}
            user={user}
            port={port}
            password={password}
            host={host}
        """)

        self.connection = await pool.acquire()
        self.cursor = await self.connection.cursor()

    async def create_tables_if_needed(self):
        await self.cursor.execute(PostgresQueries.create_notification_table)
        await self.cursor.execute(PostgresQueries.create_action_execution_history)
        await self.cursor.execute(PostgresQueries.create_contacts_table)
        await self.cursor.execute(PostgresQueries.create_banned_history)
        await self.cursor.execute(PostgresQueries.create_connection_history)

    async def remove_expired_rows(self,date,table_name,date_column_name):
        await self.cursor.execute(PostgresQueries.remove_expired_history_query(
            table_name,date_column_name),(date,))

    async def create_notification(self,name,desc,date):
        await self.cursor.execute(PostgresQueries.insert_notification,(name,desc,date))

    async def create_action_execution(self,executor,action,bot_name,type_data,date):
        await self.cursor.execute(
            PostgresQueries.insert_action_execution,(executor,action,bot_name,type_data,date))
    
    async def create_connection_history(self,name,type_data,date):
        await self.cursor.execute(PostgresQueries.insert_connection,(name,type_data,date))

    async def create_banned(self,ip):
        await self.cursor.execute(PostgresQueries.insert_banned,(ip,))

    async def get_all_rows(self,table_name):
        await self.cursor.execute(PostgresQueries.select_query(table_name))
        return await self.all_rows()
    
    async def all_rows(self):
        results = []
        async for row in self.cursor:
            results.append(row)
        return results
import asyncio
from datetime import datetime
import aiopg
import os

from .queries import PostgresQueries

class SQLHandler:

    async def gather_connection(self):
        try:
            host = "127.0.0.1"
            port = "5432"
            database = "postgres"
            user = "postgres"        
            password = 'password'

            self.connection = await aiopg.connect(
                database=database,
                user=user,
                port=port,
                password=password,
                host=host
       )

            self.cursor = await self.connection.cursor()
            self.successful_connection = True
        except Exception as e:
            print(e)
            raise e

    async def create_tables_if_needed(self):
        await self.cursor.execute(PostgresQueries.create_notification_table)
        await self.cursor.execute(PostgresQueries.create_action_execution_history)
        await self.cursor.execute(PostgresQueries.create_contacts_table)
        await self.cursor.execute(PostgresQueries.create_banned_history)
        await self.cursor.execute(PostgresQueries.create_connection_history)

    async def remove_expired_rows(self,date,table_name,date_column_name):
        await self.cursor.execute(PostgresQueries.remove_expired_history_query(
            table_name,date_column_name,date))

    async def create_notification(self,name,desc,date):
        await self.cursor.execute(PostgresQueries.insert_notification_query(name,desc,date))

    async def create_action_execution(self,executor,action,bot_name,type_data,date):
        await self.cursor.execute(
            PostgresQueries.insert_action_execution_query(executor,action,bot_name,type_data,date))
    
    async def create_connection_history(self,name,type_data,date):
        await self.cursor.execute(PostgresQueries.insert_connection_query(name,type_data,date))

    async def create_banned(self,ip):
        await self.cursor.execute(PostgresQueries.insert_banned_query(ip))
        
    async def create_contact(self,name,number):
        await self.cursor.execute(PostgresQueries.insert_contact_query(name,number))

    async def get_all_rows(self,table_name):
        await self.cursor.execute(PostgresQueries.select_query(table_name))
        return await self.all_rows()
    
    async def all_rows(self):
        results = []
        async for row in self.cursor:
            results.append(row)
        return results
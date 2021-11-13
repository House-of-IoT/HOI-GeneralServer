from sql_handler import SQLHandler
from Errors.errors import IssueConnectingToDB
class CaptureManager:
    def __init__(self,using_sql):
        self.using_sql = using_sql
        self.sql_handler = SQLHandler()

    async def try_to_gather_connection_if_needed(self):
        if self.sql_handler.connected == False:
            await self.sql_handler.gather_connection()
            if self.sql_handler.connected:
                return True
            else:
                throw 
    async def capture_contact(self,name,number):
        if self.using_sql:
            self.sql_handler.create_contact(name,number)
from datetime import datetime
from sql_handler import SQLHandler
from Errors.errors import IssueConnectingToDB
from data_catch_up_manager import DataCatchUpManager
import json
import asyncio

"""
Handles all data captures.
There are two types of data captures:

1.Storing historic data in memory.
2.Storing historic data in a database.

If the server is configured to use database:

    the capture manager accounts for connection issues by 
    allowing 5 consecutive connection attempts before going into
    in memory mode and periodically trying to regather a connection
    to the database.

    A notification is sent to all connected clients and all cached contacts.
"""

class CaptureAndServeManager:
    def __init__(self,using_sql,parent):
        self.using_sql = using_sql
        self.sql_handler = SQLHandler()
        self.failed_connection_datetimes = []
        self.currently_trying_to_connect = False
        self.catch_up_manager = DataCatchUpManager(self.sql_handler)
        self.parent = parent

    async def try_to_gather_connection_if_needed(self):
        #if we never initally connected or the was connection closed 
        if self.sql_handler.connection_status == False or self.sql_handler.connection.closed == True:
                connection_gathered = await self.sql_handler.gather_connection()
                
                #handle next steps after connection attempt
                if connection_gathered:
                    return True
                else:
                    self.failed_connection_datetimes.append(datetime.utcnow())
                    if len(self.failed_connection_datetimes) == 5:
                        self.enter_memory_capture_mode()
                    raise IssueConnectingToDB("Tried connecting to DB with no luck!")

    async def capture_contact(self,name,number,type_of_contact_capture):
        if self.using_sql:
            await self.try_to_gather_connection_if_needed()
            cursor = await self.sql_handler.connection.cursor()

            if type_of_contact_capture == "add-contact":
                await self.sql_handler.create_contact(name,number,cursor)
            else:
                pass#delete
            cursor.close()
        else:
            if type_of_contact_capture == "add-contact":
                self.parent.contacts[name] = number
            else:
                del self.parent.contacts[name]

    async def update_cached_contacts(self):
        try:
            if self.sql_handler.connection_status == True and self.sql_handler.connection.closed == False:
                cursor = await self.sql_handler.connection.cursor()
                contacts = await self.sql_handler.get_all_rows("contacts",cursor)
                contact_dict = self.convert_contacts_to_dict(contacts)
                self.write_json_to_file("contact_cache.json",contact_dict)
                cursor.close()
        except Exception as e:
            print(e)
            self.parent.console_logger.log_generic_row("Issue Caching Contacts!", "red")

    def convert_contacts_to_dict(self,contacts):
        if len(contacts) == 0 :
            return {}
        else:
            data_dict = {}
            for row in contacts:
                #key is the name, value is the number
                data_dict[row[1]] = row[2]
            return data_dict

    def write_json_to_file(self,file_name,data_dict):
            with open(file_name, "w") as file:
                file.write(json.dumps(data_dict))

    def enter_memory_capture_mode(self):
        self.using_sql = False
        self.failed_connection_datetimes = 
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.try_to_restore_connection_every_hour())

    async def attemp_reconnect_and_mode_switch(self):
        self.currently_trying_to_connect = True
        connection_gathered = await self.sql_handler.gather_connection()
        if connection_gathered:
            await self.catch_up()
            self.using_sql = True
        
        self.currently_trying_to_connect = False

    async def catch_up(self):
        await self.catch_up_manager.catch_up_action_execution(None)
        await self.catch_up_manager.catch_up_banned(None)
        await self.catch_up_manager.catch_up_connections(None)
        await self.catch_up_manager.catch_up_contacts(None)

    async def try_to_restore_connection_every_hour(self):
        while self.using_sql == False:
            await asyncio.sleep(3600)
            """
            Make sure there isn't an attempt already in progress.
            This can happen if a user manually triggers a reconnect.
            """
            if self.currently_trying_to_connect == False:
                await self.attemp_reconnect_and_mode_switch()
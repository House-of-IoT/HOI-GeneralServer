from datetime import datetime
from sql_handler import SQLHandler
from Errors.errors import IssueConnectingToDB
import os.path
import json

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

class CaptureManager:
    def __init__(self,using_sql,parent):
        self.using_sql = using_sql
        self.sql_handler = SQLHandler()
        self.failed_connection_datetimes = []
        self.in_temp_memory_mode = False
        self.parent = parent

    async def try_to_gather_connection_if_needed(self):
        #if we never initally connected or the connection closed 
        if self.sql_handler.connection_status == False or self.sql_handler.connection.closed == True:
            
            #if we haven't attempted too many reconnects(entered temp memory mode)
            if self.in_temp_memory_mode == False:
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
            if type_of_contact_capture == "add-contact":
                await self.sql_handler.create_contact(name,number)
            else:
                pass#delete
        else:
            if type_of_contact_capture == "add-contact":
                self.parent.contacts[name] = number
            else:
                del self.parent.contacts[name]

    async def update_cached_contacts(self):
        pass
        
    def enter_memory_capture_mode(self):
        pass
        
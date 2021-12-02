from datetime import datetime
from .sql_handler import SQLHandler
from Errors.errors import IssueConnectingToDB
from Errors.errors import IssueGatheringServeData
from .data_catch_up_manager import DataCatchUpManager
import traceback
import queue
import json
import asyncio
import copy

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

#PUBLIC
    async def try_to_gather_serve_target(self,target):
        try:
            type_of_data = self.map_target_to_type_of_data(target)
            return await self.serve_data(type_of_data)
        except Exception as e:
            traceback.print_exc()
            raise IssueGatheringServeData(f"while trying to gather data for {target} an error occured")

    async def try_to_route_and_capture(self,data):
        try:         
            await self.route_and_capture(data)
        except Exception as e:
            traceback.print_exc()
            #notification of failure
            self.parent.notification_handler.create_notification(
            f"Error attempting capture!",True)

#PRIVATE
    async def route_and_capture(self,data):
        if self.using_sql:
            await self.try_to_gather_connection_if_needed()
            cursor = await self.sql_handler.connection.cursor()
            await self.sql_handler.create_tables_if_needed(cursor)

            if data["type"] == "contact":
                await self.capture_contact_in_db(data,cursor)
            elif data["type"] == "banned":
                await self.capture_banned_in_db(data,cursor)
            elif data["type"] == "executed_action":
                await self.sql_handler.create_action_execution(
                    data["data"]["executor"],data["data"]["action"],
                    data["data"]["bot_name"],data["data"]["bot_type"],
                    data["data"]["date"],cursor)
            elif data["type"] == "connection":
                await self.sql_handler.create_connection_history(
                    data["data"]["name"]
                    ,data["data"]["type"],
                    data["data"]["date"],cursor)
        else:
            self.capture_in_memory(data)

    async def capture_contact_in_db(self,data,cursor):
        if await self.row_exist_in_db(data["data"]["name"],cursor,"contacts","name") and data["data"]["type"] == "add-contact":
            return
        if data["data"]["type"] == "add-contact":
            name = data["data"]["name"]
            number = data["data"]["number"]
            await self.sql_handler.create_contact(          
                name,
                number,
                cursor)
            self.parent.notification_handler.create_notification(
            f"New contact added to server {name}({number})!",False)
        else:
            await self.sql_handler.execute_single_parameter_delete_query(
                "contacts",
                "name",
                data["data"]["name"],
                cursor)

    async def capture_banned_in_db(self,data,cursor):
        if await self.row_exist_in_db(data["data"]["ip"],cursor,"banned","Ip") and data["data"]["type"] == "add":
            return 
        if data["data"]["type"] == "add-banned-ip":
            await self.sql_handler.create_banned(data["data"]["ip"],cursor)
        else:
            await self.sql_handler.execute_single_parameter_delete_query(
                "banned",
                "Ip",
                data["data"]["ip"],
                cursor)

    def capture_in_memory(self,data):
        if data["type"] == "contact":
            self.capture_in_dict(
                self.parent.contacts,data["data"]["name"],
                data["data"]["number"],
                "add-contact",
                data)
        elif data["type"] == "connection":
            self.capture_generic_for_queue_in_memory(data,self.parent.most_recent_connections,20)
        elif data["type"] == "executed_action":
            self.capture_generic_for_queue_in_memory(data,self.parent.most_recent_executed_actions,15)
        elif data["type"] == "banned":
            self.capture_in_dict(
                self.parent.failed_auth_attempts,
                data["data"]["ip"],
                4, # more than three failed attempts means you are banned
                "add-banned-ip",
                data)
            print(self.parent.failed_auth_attempts)

    def capture_in_dict(self,dict_obj,key,value,add_op_code,data):
        if data["data"]["type"] == add_op_code:
            dict_obj[key] = value
        else:
            if key in dict_obj:
               del dict_obj[key]

    def capture_generic_for_queue_in_memory(self,data,queue_obj,max_size):
        if queue_obj.qsize() > max_size:
            queue_obj.get()
        queue_obj.put(data["data"])
    
    async def serve_data(self,type_of_data):
        if self.using_sql:
            await self.try_to_gather_connection_if_needed()
            cursor = await self.sql_handler.connection.cursor()
            data = await self.sql_handler.get_all_rows(type_of_data,cursor)
            cursor.close()
            correctly_formatted_data = self.convert_data_to_expected_type(data,type_of_data)
            return correctly_formatted_data
        else:
            return self.serve_data_from_memory(type_of_data)
    
    """
    creating deep copies of certain object due to
    the date stringification that happens after data gather.
    This avoids overwriting the original copy in memory.
    """
    def serve_data_from_memory(self,type_of_data):
        if type_of_data == "contacts":
            return self.parent.contacts
        elif type_of_data == "banned":
            return self.parent.banned_ips()
        elif type_of_data == "actions":
            queue_copy_and_list_copy = self.convert_queue_to_list_and_create_queue_copy(self.parent.most_recent_executed_actions)
            self.parent.most_recent_executed_actions = queue_copy_and_list_copy[0]
            return copy.deepcopy(queue_copy_and_list_copy[1])
        elif type_of_data == "connections":
            queue_copy_and_list_copy = self.convert_queue_to_list_and_create_queue_copy(self.parent.most_recent_connections)
            self.parent.most_recent_connections = queue_copy_and_list_copy[0]
            return copy.deepcopy(queue_copy_and_list_copy[1])

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

    async def update_cached_contacts(self):
        while True:
            if self.using_sql:
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
        if len(contacts) == 0:
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
        self.failed_connection_datetimes = []
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.try_to_restore_connection_every_half_hour())

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

    async def try_to_restore_connection_every_half_hour(self):
        while self.using_sql == False:
            await asyncio.sleep(1800)
            """
            Make sure there isn't an attempt already in progress.
            This can happen if a user manually triggers a reconnect.
            """
            if self.currently_trying_to_connect == False:
                await self.attemp_reconnect_and_mode_switch()

    async def row_exist_in_db(self,parameter,cursor,table_name,col_name):
        rows_in_db = await self.sql_handler.get_all_rows_single_parameter(
            table_name,
            col_name,
            parameter,
            cursor)
        if len(rows_in_db) == 0:
            return False
        else:
            return True

    def convert_data_to_expected_type(self,data,type_of_data):
        if type_of_data == "contacts":
            return self.structure_contact_data(data)
        elif type_of_data == "connections":
            return self.structure_connection_data(data)
        elif type_of_data == "actions":
            return self.structure_action_execution_data(data)
        elif type_of_data == "banned":
            return self.structure_banned_data(data)

    def structure_contact_data(self,data):
        data_holder = {}
        for contact in data:
            data_holder[contact[1]] = contact[2]
        return data_holder
        
    def structure_action_execution_data(self,data):
        data_holder = []
        for action_execution in data:
            data_dict = {
                "executor":action_execution[1], 
                "action":action_execution[2], 
                "bot_name": action_execution[3], 
                "bot_type":action_execution[4],
                "date":action_execution[5]}
            data_holder.append(data_dict)
        return data_holder

    def structure_connection_data(self,data):
        data_holder = []
        for connection in data:
            data_dict = {
                "name":connection[1], 
                "type":connection[2], 
                "date":connection[3]}
            data_holder.append(data_dict)
        return data_holder

    def structure_banned_data(self,data):
        data_holder = set()
        for banned in data:
            data_holder.add(banned[1])
        return data_holder

    def convert_queue_to_list(self,target_queue):
        result = []
        while target_queue.qsize() > 0:
            result.append(target_queue.get())
        return result

    def convert_queue_to_list_and_create_queue_copy(self,old_queue):
        new_queue = queue.Queue()
        new_list = []

        while old_queue.qsize()>0:
            queue_value = old_queue.get()
            new_queue.put(queue_value)
            new_list.append(queue_value)
        return (new_queue,new_list)
    
    """ Converts opcode that comes from client to the table name in the db"""
    def map_target_to_type_of_data(self,target):
        if target == "servers_banned_ips":
            return "banned"
        elif target == "recent_connections":
            return "connections"
        elif target == "executed_actions":
            return "actions"
        else:
            return "contacts"
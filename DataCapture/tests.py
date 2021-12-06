from os import name
import unittest
from datetime import datetime
from sql_handler import SQLHandler
from capture_object_creator import CaptureDictCreator

"""
The tests below requires the following env variables
    host  -> ("hoi_db_host"),
    port -> ("hoi_db_port")
    database -> ("hoi_db_name")
    user -> ("hoi_db_user")        
    password  -> ("hoi_db_pw")

The tests below must be done on a clean database.

The easiest way to get a clean database would be to spin up a new 
postgres docker container that is configured to the above env variables.

"""

class AsyncTests(unittest.IsolatedAsyncioTestCase):

    async def test(self):
        handler = SQLHandler()
        await handler.gather_connection()
        self.cursor = await handler.connection.cursor()
        try:
            await handler.gather_connection()
            await handler.create_tables_if_needed()
            await self.contact_insertion(handler)
            await self.banned_insertion(handler)
        except Exception as e:
            await handler.connection.close()
            raise e

    async def contact_insertion(self,handler):
        print("testing contact insertion...")
        contacts = await handler.get_all_rows("contacts",self.cursor)
        print(contacts)
        self.assertEqual(len(contacts),0)
        await handler.create_contact("test","12399239923932",self.cursor)

        contacts = await handler.get_all_rows("contacts",self.cursor)
        self.assertEqual(len(contacts),1)

        #is the data correct?
        self.assertEqual(contacts[0][1],"test")
        self.assertEqual(contacts[0][2],"12399239923932")

    async def banned_insertion(self,handler):
        print("testing banned insertion...")
        ips = await handler.get_all_rows("banned",self.cursor)
        self.assertEqual(len(ips),0)

        await handler.create_banned("293.212.23123.1",self.cursor) 

        ips = await handler.get_all_rows("banned",self.cursor)

        self.assertEqual(len(ips),1)

        self.assertEqual(ips[0][1],"293.212.23123.1",self.cursor)

class Tests(unittest.TestCase):
    def test(self):
        self.test_action_capture_dict()
        self.test_contact_capture_dict()
        self.test_banned_capture_dict()
        self.test_connection_capture_dict()
    
    def test_action_capture_dict(self):
        print("testing action capture dict...")
        client_name = "test1"
        bot_name = "test2"
        action = "test3"
        bot_type = "test4"

        result = CaptureDictCreator.create_action_dict(client_name,bot_name,action,bot_type)
        self.assertEqual(result["executor"],client_name)
        self.assertEqual(result["bot_name"],bot_name)
        self.assertTrue("date" in result)
        self.assertEqual(result["bot_type"],bot_type)
        self.assertEqual(result["action"],action)
    
    def test_contact_capture_dict(self):
        print("testing contact capture dict...")
        name = "test_1"
        number = "8812282929"
        #may not be the real op code used
        add_or_remove = "remove"

        result = CaptureDictCreator.create_contact_dict(name,number,add_or_remove)

        self.assertEqual(result["type"],add_or_remove)
        self.assertEqual(result["number"],number)
        self.assertEqual(result["name"],name)

    def test_banned_capture_dict(self):
        print("testing banned ip capture dict...")
        ip = "127.0.0.1"
        type_data = "add"
        result = CaptureDictCreator.create_banned_dict(ip,type_data)
        self.assertEqual(result["ip"],ip)
        self.assertEqual(result["type"],type_data)

    def test_connection_capture_dict(self):
        print("testing connection capture dict...")
        name = "test1"
        type_data = "non-bot"
        result = CaptureDictCreator.create_connection_dict(name,type_data)
        self.assertEqual(result["name"],name)
        self.assertEqual(result["type"],type_data)

if __name__ == "__main__":
    unittest.main()
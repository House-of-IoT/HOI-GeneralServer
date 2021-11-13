from os import name
import unittest
from datetime import datetime
from sql_handler import SQLHandler


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

class Tests(unittest.IsolatedAsyncioTestCase):

    async def test(self):
        handler = SQLHandler()
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
        ips = await handler.get_all_rows("banned",self.cursor)
        self.assertEqual(len(ips),0)

        await handler.create_banned("293.212.23123.1",self.cursor) 

        ips = await handler.get_all_rows("banned",self.cursor)

        self.assertEqual(len(ips),1)

        self.assertEqual(ips[0][1],"293.212.23123.1",self.cursor)

if __name__ == "__main__":
    unittest.main()
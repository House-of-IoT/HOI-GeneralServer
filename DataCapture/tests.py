from logging import Handler
import unittest
import asyncio
from datetime import datetime
from sql_handler import SQLHandler

"""
The tests below requires the following env variables
    host  -> ("db_h"),
    port -> ("db_p")
    database -> ("HOI")
    user -> ("HOI_USER")        
    password  -> ("HOI_PW")

The tests below must be done on a clean database.

The easiest way to get a clean database would be to spin up a new 
postgres docker container that is configured to the above env variables.

"""

class Tests(unittest.IsolatedAsyncioTestCase):

    async def test(self):
        handler = SQLHandler()
        await handler.gather_connection()

    async def contact_insertion(self,handler):
        contacts = handler.get_all_rows("contacts")
        self.assertEqual(len(contacts),0)
        handler.create_contact("test","12399239923932")

        contacts = handler.get_all_rows("contacts")
        self.assertEqual(len(contacts),1)

        #is the data correct?
        self.assertEqual(contacts[0][0],"test")
        self.assertEqual(contacts[0][1],"12399239923932")

    async def banned_insertion(self,handler):
        ips = await handler.get_all_rows("banned")
        self.assertEqual(len(ips),0)

        await handler.create_banned("293.212.23123.1") 

        ips = await handler.get_all_rows("banned")

        self.assertEqual(len(ips),1)

        self.assertEqual(ips[0][1],"293.212.23123.1")

    async def notification_insertion(self,handler):
        notifications = await handler.get_all_rows("notifications")
        self.assertEqual(len(notifications),0)

        date = datetime.utcnow()
        await handler.create_notification("test","random_notification",date)

        notifications = await handler.get_all_rows("notifications")

        self.assertEqual(len(notifications),1)

        self.assertEqual(notifications[0][1],"test")
        self.assertEqual(notifications[0][2],"random_notification")
        self.assertEqual(notifications[0][3],date)


    async def create_contact(self,handler):
        contacts = await handler.get_all_rows("contacts")
        self.assertEqual(len(contacts),0)

        await handler.create_contact("test","18829389282")

        contacts = await handler.get_all_rows("contacts")

        self.assertEqual(len(contacts),1)

        self.assertEqual(contacts[0][1],"test")
        self.assertEqual(contacts[0][2],"18829389282")
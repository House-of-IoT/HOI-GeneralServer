
import unittest
import asyncio
import websockets
import json
import unittest

'''
This test assumes
1.Your server follows the correct protocol
2.Your server has one bot connected by the name of test and no 'non-bots' connected
3.You will not run into any networking errors
4.Your server is hosted locally on port 50223
The intended way to run this test is to run the test_bot_client first.
5.The server config settings match the hard coded default ones in config.py's 'ConfigHandler'
'''

'''
Protocol

1.Send password for general server
2.Send name and type(json serialized)
3.Send your naming of the server
4.check server response
5.begin general sequence
'''

class AsyncTests(unittest.IsolatedAsyncioTestCase):
    connected_viewing_done = False
    
    async def test(self):
        websocket = await self.connect(need_websocket=True)
        await self.view_state_deactivated_bots(websocket)
        await asyncio.sleep(5)
        await self.activate_and_deactivate_and_basic_data(websocket)
        await asyncio.sleep(5)
        await self.viewing_connected_devices(websocket)
        await asyncio.sleep(5)
        await self.disconnect_bot(websocket) 

    async def connect(self,need_websocket = False):
        websocket = await websockets.connect('ws://192.168.1.109:50223', ping_interval= None, max_size = 20000000)
        await websocket.send("")
        await websocket.send(self.name_and_type())
        await websocket.send("test_name")
        connection_response = await websocket.recv()
        if need_websocket:
            return websocket
        else:
            return connection_response

    async def add_and_view_contacts():
        pass

    #assumes that one bot named "test" is connected to the server
    async def view_state_deactivated_bots(self,websocket):
        await asyncio.sleep(5)
        await self.deactivate_without_auth(websocket)
        viewing_data = await self.send_and_handle_viewing(websocket,"servers_deactivated_bots")
        print(viewing_data)
        self.assertTrue("test" in viewing_data["target_value"][0])
        await self.activate_with_auth(websocket)

    #this test is repeating logic but ensures the bot is responding after re-activation via 'basic data'
    async def activate_and_deactivate_and_basic_data(self,websocket):
        await asyncio.sleep(5)
        await self.deactivate_without_auth(websocket)
        await self.activate_with_auth(websocket)
        await self.basic_data(websocket,1)

    async def viewing_connected_devices(self,websocket):
        viewing_data = await self.send_and_handle_viewing(websocket,"servers_devices")
        self.assertEqual(viewing_data["target"] ,"servers_devices")
        self.assertTrue("test1" in  json.loads(viewing_data["target_value"]))
        self.assertTrue( json.loads(viewing_data["target_value"])["test1"] == "non-bot")
        self.connected_viewing_done = True

    #assumes there is a bot connected by the name of "test"
    async def disconnect_bot(self,websocket):
        await self.send_bot_control(websocket,"disconnect")
        response = await websocket.recv()
        data_dict = json.loads(response)
        self.assert_basic_response(data_dict,"disconnect","success","test")
        await self.basic_data(websocket,0)

    #assumes there are 'bot_num' amount of bots connected
    async def basic_data(self,websocket,bot_num):
        await websocket.send("basic_data")
        response = await websocket.recv()
        data_dict = json.loads(response)
        self.assertEqual(data_dict["server_name"],"test_name")
        self.assertEqual(len(data_dict["bots"]),bot_num)
        
    async def send_bot_control(self,websocket,action):
        await websocket.send("bot_control")
        await websocket.send(action)
        await websocket.send("test")

    async def send_auth(self,websocket,action,expected_bot_name):
        await websocket.send("")#default password
        response = await websocket.recv()
        
        response_data_dict = json.loads(response)
        self.assert_basic_response(response_data_dict,action,"success",expected_bot_name)
        return response_data_dict

    async def send_and_handle_viewing(self,websocket,target):
        await websocket.send(target)
        response = await websocket.recv()
        activate_data_dict = json.loads(response)
        self.assert_basic_response(activate_data_dict,"viewing","needs-admin-auth",None)
        viewing_data = await self.send_auth(websocket,"viewing",None)
        return viewing_data 

    async def deactivate_without_auth(self,websocket):
        await self.send_bot_control(websocket,"deactivate")
        response = await websocket.recv()
        deactivate_data_dict = json.loads(response)
        self.assert_basic_response(deactivate_data_dict,"deactivate","success","test")

    async def activate_with_auth(self,websocket):
        #activate with authentication
        await self.send_bot_control(websocket,"activate")
        response = await websocket.recv()
        activate_data_dict = json.loads(response)
        self.assert_basic_response(activate_data_dict,"activate","needs-admin-auth",None)
        await self.send_auth(websocket,"activate","test")
    
    def name_and_type(self):
        data = {"name":"test1" , "type":"non-bot"}
        return json.dumps(data)

    def assert_basic_response(self,data_dict,action,expected_status,expected_bot_name):
        self.assertEqual(data_dict["server_name"],"test_name")
        self.assertEqual(data_dict["action"],action)
        self.assertEqual(data_dict["status"],expected_status)
        self.assertEqual(data_dict["bot_name"],expected_bot_name)

if __name__ == "__main__":
    unittest.main()
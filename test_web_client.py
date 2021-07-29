
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

    async def test_connect(self):
        await asyncio.sleep(5)
        response = await self.connect()
        self.assertEqual("success",response)

    #assumes there is a bot connected by the name of test
    #assumes the server's deactivate action requires admin authentication
    async def test_activate_and_deactivate(self):
        await asyncio.sleep(5)
        websocket = await self.connect(need_websocket=True)

        #deactivate with authentication
        await self.send_bot_control(websocket,"deactivate")
        response = await websocket.recv()
        print(response)
        deactivate_data_dict = json.loads(response)
        self.assert_basic_response(deactivate_data_dict,"deactivate","needs-admin-auth",None)
        await self.send_auth(websocket,"deactivate")

        #activate without authetication
        await self.send_bot_control(websocket,"activate")
        response = await websocket.recv()
        activate_data_dict = json.loads(response)
        self.assert_basic_response(activate_data_dict,"activate","success","test")
        
        # test basic data after activate to make sure it is responding
        await self.basic_data(websocket,1)

    #assumes there is a bot connected by the name of "test"
    async def test_disconnect(self):
        await asyncio.sleep(5)
        websocket = await self.connect(need_websocket=True)
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
        print(data_dict)
        self.assertEqual(data_dict["server_name"],"test_name")
        self.assertEqual(len(data_dict["bots"]),bot_num)
        
    async def send_bot_control(self,websocket,action):
        await websocket.send("bot_control")
        await websocket.send(action)
        await websocket.send("test")

    async def send_auth(self,websocket,action):
        await websocket.send("")#default password
        response = await websocket.recv()
        print(response)
        
        response_data_dict = json.loads(response)
        print(response_data_dict)
        self.assert_basic_response(response_data_dict,action,"success","test")

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
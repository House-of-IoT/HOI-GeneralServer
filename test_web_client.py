
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
        websocket = await websockets.connect('ws://localhost:50223', ping_interval= None, max_size = 20000000)
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
    async def test_activate_and_deactivate(self):
        await asyncio.sleep(5)
        websocket = await self.connect(need_websocket=True)

        await self.send_bot_control(websocket,"deactivate")
        response = await websocket.recv()
        deactivate_data_dict = json.loads(response)
        self.test_basic_response_success(deactivate_data_dict,"deactivate")

        await asyncio.sleep(5)
        await self.send_bot_control(websocket,"activate")
        response = await websocket.recv()
        activate_data_dict = json.loads(response)
        self.test_basic_response_success(activate_data_dict,"activate")

    #assumes there is a bot connected by the name of "test"
    async def test_disconnect(self):
        await asyncio.sleep(5)
        websocket = await self.connect(need_websocket=True)
        await self.send_bot_control(websocket,"disconnect")
        response = await websocket.recv()
        data_dict = json.loads(response)
        self.test_basic_response_success(data_dict,"disconnect")
        await self.basic_data(websocket)

    #assumes there are no bots connected(included in test_disconnect)
    async def basic_data(self,websocket):
        await asyncio.sleep(5)
        await websocket.send("basic_data")
        response = await websocket.recv()
        data_dict = json.loads(response)
        print(data_dict)
        self.assertEqual(data_dict["server_name"],"test_name")
        self.assertEqual(len(data_dict["bots"]),0)
        
    async def send_bot_control(self,websocket,action):
        await websocket.send("bot_control")
        await websocket.send(action)
        await websocket.send("test")

    def name_and_type(self):
        data = {"name":"test1" , "type":"non-bot"}
        return json.dumps(data)

    def test_basic_response_success(self,data_dict,action):
        self.assertEqual(data_dict["server_name"],"test_name")
        self.assertEqual(data_dict["action"],action)
        self.assertEqual(data_dict["status"],"success")
        self.assertEqual(data_dict["bot_name"],"test")



if __name__ == "__main__":
    unittest.main()
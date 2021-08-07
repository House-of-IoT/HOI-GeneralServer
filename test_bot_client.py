import asyncio
import websockets
import json
import unittest

'''
Note: This test bot client 
is really just the second part to
the test_web_client , this bot only
truly tests the responses to authentication
since each bot is unique it is and doesn't really 
recv data other than requests from the web_client (that vary), there is 
hardly anything to assert
'''

'''
The following test assumes
1.Your server follows the correct protocol
2.There are no bots connect with the name of 'test'
3.There will be no networking interruptions
4.Your server is hosted locally on port 50223
'''

'''
protocol

1.Send password for general server
2.Send name and type(json serialized)
3.Send your naming of the server
4.check server response
5.begin general sequence
'''

class AsyncTests(unittest.IsolatedAsyncioTestCase):
    
    async def connect(self):
        websocket = await websockets.connect('ws://192.168.1.109:50223', ping_interval= None, max_size = 20000000)
        await websocket.send("")
        await websocket.send(self.name_and_type())
        await websocket.send("test_name")
        connection_response = await websocket.recv()
        self.assertEqual(connection_response,"success")
        return websocket

    async def test(self):
        websocket = await self.connect()
        await self.send_periodic_data_and_listen(websocket)

    async def send_periodic_data_and_listen(self,websocket):
        while True:
            try:
                await websocket.send(json.dumps({"data":"","alert_status":"alert_present", "message":"test"})) #basic data
                message = await asyncio.wait_for(websocket.recv(),5)
                if message == "deactivate":
                    await websocket.send("success")
                    await self.enter_deactivate_loop(websocket)
                elif message == "disconnect":
                    await websocket.send("success")
                    print("disconnecting.")
                    break

            except Exception as e: 
                print(e)

    async def enter_deactivate_loop(self,websocket):
        while True:
            try:
                message = await asyncio.wait_for(websocket.recv(),5)
                print(message)
                if message == "activate":
                    await websocket.send("success")
                    break
            except Exception as e:
                print(e)

    def name_and_type(self):
        data = {"name":"test" , "type":"reed_switch"}
        return json.dumps(data)

if __name__ == "__main__":
    unittest.main()
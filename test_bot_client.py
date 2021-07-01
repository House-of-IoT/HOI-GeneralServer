
import unittest
import asyncio
import websockets
import json

'''
1.Send password for general server
2.Send name and type(json serialized)
3.Send your naming of the server
4.check server response
5.begin general sequence
'''

class Test:
    
    def __init__(self):
        self.active = True

    async def test_connect(self):
        websocket = await websockets.connect('ws://localhost:50223'  ,  ping_interval= None  , max_size = 20000000)
        await websocket.send("")
        await websocket.send(self.name_and_type())
        await websocket.send("server_test")

        connection_response = await websocket.recv()
        if connection_response != "success":
            print("auth_test_failed")
            print(f"expected success , got:{connection_response}")
        else:
            print("auth_passed")
            await self.test_send_periodic_data_and_listen(websocket)

    async def test_send_periodic_data_and_listen(self,websocket):
        while True:
            try:
                message = await asyncio.wait_for(websocket.recv(),5)
                if message == "basic_data":
                    # simulating the basic data
                    await websocket.send("") 
                elif message == "deactivate"
                print(message)
            except Exception as e: 
                print(e)
                #handle socket closed
                #break

    def name_and_type(self):
        data = {"name":"test" , "type":"reed_switch"}
        return json.dumps(data)

if __name__ == "__main__":
    main = Test();
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main.test_connect())
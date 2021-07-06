
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
    
    async def test_connect(self):
        websocket = await websockets.connect('ws://localhost:50223'  ,  ping_interval= None  , max_size = 20000000)
        await websocket.send("")
        await websocket.send(self.name_and_type())
        await websocket.send("test_name")
        connection_response = await websocket.recv()
        if connection_response != "success":
            print("auth_test_failed")
            print(f"expected success , got:{connection_response}")
        else:
            print("auth_passed")
            while True:
                pass

    def name_and_type(self):
        data = {"name":"test1" , "type":"non-bot"}
        return json.dumps(data)

if __name__ == "__main__":
    main = Test();
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main.test_connect())

import unittest
import asyncio
import websockets
import json

'''
1.Send password for general server
2.Send name and type(json serialized)
3.check server response
4.begin general sequence
'''


class Test:
    
    async def test_connect(self):
        websocket = await websockets.connect('ws://localhost:50223'  ,  ping_interval= None  , max_size = 20000000)
        await websocket.send("")
        await websocket.send(self.name_and_type())
        connection_response = await websocket.recv()
        if connection_response != "success":
            print("auth_test_failed")
            print(f"expected success , got:{connection_response}")
        else:
            print("auth_passed")


    def name_and_type(self):
        data = {"name":"test1" , "type":"non-bot"}
        return json.dumps(data)

if __name__ == "__main__":
    main = Test();
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main.test_connect())
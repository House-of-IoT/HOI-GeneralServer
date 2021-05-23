import asyncio
import json
import websockets
import time
from type_capabilities import Capabilities
class Main:
    def __init__(self):
        self.host = '127.0.0.1' 
        self.port = 50223
        self.clients = {}
        self.clients_type = {}
        
        self.accepted_types = {
            "reed_switch":Capabilities() , 
            "gas_smoke_fire_detector" :Capabilities(), 
            "ralph" : Capabilities(
                has_audio_streaming=True, 
                has_ground_movement=True) , 
            "home_watcher" : Capabilities(
                has_audio_streaming=True,
                has_video_streaming=True,
                has_pir=True),
            "non-bot" :Capabilities()}

        self.connected = 0
        self.clients_on_timer = {}

    def name_and_type(self, response):
        try:
            data_dict = json.loads(response)
            if "name" in data_dict and "type" in data_dict:
                return (data_dict["name"] , data_dict["type"])
            else:
                return None
        except: # json parsing 
            return None 

    async def route_type(self,websocket,name,client_type):
        try:
            if client_type in self.accepted_types:
                self.clients[name] = websocket
                self.clients_type[name] = client_type
                await websocket.send("success")
            else:
                await websocket.send("error_invalid_type")
        except:
            pass
    
    async def check_declaration(self,websocket , path):
        try:
            type_of_client = await asyncio.wait_for(websocket.recv(), 1)
            name_and_type = self.name_and_type(type_of_client)

            # Name and type exists/there is no client with this name
            if name_and_type != None and name_and_type[0] not in self.clients:
                await self.route_type(websocket,name_and_type[0],name_and_type[1])     
             
        except:
            pass

    def start_server(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(websockets.serve(self.check_declaration,self.host,self.port,ping_interval=None))
        loop.run_forever()
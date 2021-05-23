import asyncio
import json
import websockets
import time

class Main:
    def __init__(self):
        self.host = '127.0.0.1' 
        self.port = 50223
        self.clients = {}
        self.clients_type = {}
        self.accepted_types = {"reed_switch" , 
            "gas_smoke_fire_detector" , "ralph" , "home_watcher"}
        self.connected = 0
        self.clients_on_timer = {}

    async def check_type(self):
        pass
    
    async def disconnect(self):
        pass

    def name_and_type(self, response):
        data_dict = json.loads(response)
        if "name" in data_dict and "type" in data_dict:
            return (data_dict["name"] , data_dict["type"])
        else:
            return None

    async def route_type(self,websocket,name,client_type):
        pass

    async def check_declaration(self,websocket , path):
        try:
            type_of_client = await asyncio.wait_for(websocket.recv(), 1)
            name_and_type = self.name_and_type(type_of_client)

            # Name and type exists/there is no client with this name
            if name_and_type != None and name_and_type[0] not in self.clients:
                self.route_type(websocket,name_and_type[0],name_and_type[1])     
             
        except:
            pass# connection goes out of scope


    def start_server(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(websockets.serve(self.check_declaration,self.host,self.port,ping_interval=None))
        loop.run_forever()
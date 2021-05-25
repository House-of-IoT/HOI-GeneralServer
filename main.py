import asyncio
import json
import websockets
from type_capabilities import Capabilities

class Main:

    def __init__(self):
        self.host = '127.0.0.1' 
        self.port = 50223
        self.devices = {}
        self.devices_type = {}
        self.failed_admin_attempts = {}
        self.admin_password = ""

        self.accepted_types = {
            "reed_switch":Capabilities() , 
            "gas_smoke_fire_detector":Capabilities(), 
            "ralph":Capabilities(
                has_audio_streaming=True, 
                has_ground_movement=True) , 
            "home_watcher":Capabilities(
                has_audio_streaming=True,
                has_video_streaming=True,
                has_pir=True),
            "non-bot":Capabilities()}
        self.connected = 0

    def name_and_type(self, response):
        try:
            data_dict = json.loads(response)
            if "name" in data_dict and "type" in data_dict:
                return (data_dict["name"] , data_dict["type"])
            else:
                return None
        except: 
            return None 

    def handle_client():
        pass

    def handle_bot():
        pass

    def next_steps(self,client_type, name,websocket):
        if client_type == "non-bot":
            pass
        else:
            pass

    async def handle_type(self,websocket,name,client_type):
        try:
            if client_type in self.accepted_types:
                self.clients[name] = websocket
                self.clients_type[name] = client_type
                await websocket.send("success")
                self.next_steps(client_type,name,websocket)
            else:
                await websocket.send("error_invalid_type")
        except:
            pass

    async def check_declaration(self,websocket , path):
        try:
            if self.is_banned(str(websocket.remote_address[0])):
                return
            type_of_client = await asyncio.wait_for(websocket.recv(), 1)
            name_and_type = self.name_and_type(type_of_client)

            # Name and type exists/there is no client with this name
            if name_and_type != None and name_and_type[0] not in self.clients:
                await self.handle_type(websocket,name_and_type[0],name_and_type[1])     
        except:
            pass

    def is_banned(self,ip):
        if ip in self.failed_admin_attempts:
            if self.failed_admin_attempts[ip] > 3:
                return True
            else:
                return False
        return False

    def is_admin(self,password,websocket):
        if password == self.admin_password:
            return True
        else:
            ip = str(websocket.remote_address[0])
            if ip in self.failed_admin_attempts:
                self.failed_admin_attempts[ip] +=1
            else:
                self.failed_admin_attempts[ip] = 1
            return False

    async def reset_attempts(self):
        await asyncio.sleep(86400)# one day
        self.failed_admin_attempts = {}

    def start_server(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(websockets.serve(self.check_declaration,self.host,self.port,ping_interval=None))
        loop.run_forever()
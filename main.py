import asyncio
import json
import websockets
from type_capabilities import Capabilities
from client_handler import ClientHandler
from device_handler import DeviceHandler

class Main:

    def __init__(self):
        self.host = '127.0.0.1' 
        self.port = 50223
        self.devices = {}
        self.devices_type = {}
        self.failed_admin_attempts = {}
        self.available_status = {}
        self.deactivated_bots = set()
        self.stream_mode_status= {}
        self.outside_names = {}
        self.admin_password = ""#move to env
        self.regular_password = ""#move to env
        self.device_handler = DeviceHandler(self)

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

    async def handle_client(self,websocket,name):
        while True:
            await asyncio.sleep(1)
            try:
                handler = ClientHandler(self,name,websocket)
                request = await websocket.recv()
                if request == "bot_control":
                    await handler.gather_request_for_bot()
                else:
                    await self.device_handler.get_and_send_passive_data(name)
                
            except Exception as e:
                print(e)
                del self.devices[name]
                del self.devices_type[name]
                break      
    
    async def handle_bot(self,websocket,name):
        while True:
            try:
                if name not in self.devices:
                    break
                await websocket.send("--heartbeat--")
                await asyncio.sleep(60)
            except Exception as e:
                #issue sending to websocket
                print(e)
                del self.devices[name]
                del self.devices_type[name]
                break

    async def next_steps(self,client_type, name,websocket):
        if client_type == "non-bot":
            await self.handle_client(websocket,name)
        else:
            await self.handle_bot(websocket,name)

    async def handle_type(self,websocket,name,client_type):
        try:
            if client_type in self.accepted_types:
                self.devices[name] = websocket
                self.devices_type[name] = client_type
                await websocket.send("success")
                await self.next_steps(client_type,name,websocket)
            else:
                await websocket.send("error_invalid_type")
        except:
            pass

    async def check_declaration(self,websocket , path):
        try:     
            if self.is_banned(str(websocket.remote_address[0])):
                return
            if await self.is_authed(websocket):
                print("here")
                type_of_client = await asyncio.wait_for(websocket.recv(), 1)
                name_and_type = self.name_and_type(type_of_client)
                outside_name = await asyncio.wait_for(websocket.recv(),1)

                # Name and type exists/there is no client with this name
                if name_and_type != None and name_and_type[0] not in self.devices:
                    self.outside_names[name_and_type[0]] = outside_name
                    await self.handle_type(websocket,name_and_type[0],name_and_type[1]) 
                else:
                    await websocket.send("issue")
            else:
                await websocket.send("issue")    
        except Exception as e:
            print(e)

    def is_banned(self,ip):
        if ip in self.failed_admin_attempts:
            if self.failed_admin_attempts[ip] > 3:
                return True
            else:
                return False
        return False

    async def is_authed(self,websocket):
        try:
            password = await asyncio.wait_for(websocket.recv(),5)
            if password == self.regular_password:
                return True
            else:
                self.add_to_failed_attempts(websocket)
                return False
        except:
            self.add_to_failed_attempts(websocket)
        
    def is_admin(self,password,websocket):
        if password == self.admin_password:
            return True
        else:
            self.add_to_failed_attempts(websocket)
            return False

    def add_to_failed_attempts(self,websocket):
        ip = str(websocket.remote_address[0])
        if ip in self.failed_admin_attempts:
            self.failed_admin_attempts[ip] +=1
        else:
            self.failed_admin_attempts[ip] = 1

    async def reset_attempts(self):
        await asyncio.sleep(86400)# one day
        self.failed_admin_attempts = {}

    def start_server(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            websockets.serve(self.check_declaration,self.host,self.port,ping_interval=None))
        loop.run_forever()

Main().start_server()
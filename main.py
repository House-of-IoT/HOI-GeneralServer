from BasicResponse import BasicResponse
import asyncio
import json
import websockets
import datetime
import websockets
from errors import AddressBannedException
from type_capabilities import Capabilities
from client_handler import ClientHandler
from device_handler import DeviceHandler
from colorama import init
from console_logging import ConsoleLogger
from twilio_handler import TwilioHandler
from config import ConfigHandler
import traceback

class Main:
    def __init__(self):
        init()#for windows
        self.host = '192.168.1.109' 
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
        self.super_admin_password = ""#move to env
        self.device_handler = DeviceHandler(self)
        self.admins = {} #used to determine who is an admin , for UI disconnecting
        self.last_alert_sent = {}
        self.console_logger = ConsoleLogger(self)
        self.twilio_handler = TwilioHandler()
        self.alerts_enabled = True
        self.config = ConfigHandler() #causes exit if config isn't correct
        self.bot_passive_data = {}

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
            "infared":Capabilities(),
            "non-bot":Capabilities()}

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
                print(request)
                if request == "bot_control":
                    await handler.gather_request_for_bot()
                elif request == "servers_devices":
                    await handler.send_table_state(self.devices_type,"servers_devices","both")
                elif request == "servers_deactivated_bots":
                    await handler.send_table_state(self.deactivated_bots,"servers_deactivated_bots","values-set")
                elif request == "servers_banned_ips":
                    await handler.send_table_state(self.banned_ips(),"servers_banned_ips","values-set")
                elif request == "server_config":
                    await handler.send_server_config()
                elif request == "passive_data":
                    await self.device_handler.get_and_send_passive_data(name)
                else:
                    await self.route_client_advanced_request(handler,request)             
                
            except Exception as e:
                print(f"here:{e}")
            
                del self.devices[name]
                del self.devices_type[name]
                self.console_logger.log_disconnect(name)
                traceback.print_exc()
                break      
    
    async def handle_bot(self,websocket,name):
        self.available_status[name] = True
        while True:
            try:
                if name not in self.devices:
                    break
                if self.alerts_enabled and self.alert_will_not_be_spam(name) and self.there_are_only_bots():
                    self.available_status[name] = False
                    await self.check_for_alert(websocket,name)
                if self.available_status[name] == True:
                    await self.try_to_gather_bot_passive_data(name,websocket)

                await asyncio.sleep(5)
            except Exception as e:
                #issue sending to websocket
                del self.devices[name]
                del self.devices_type[name]
                self.console_logger.log_disconnect(name)
                traceback.print_exc()
                break

    async def next_steps(self,client_type, name,websocket):
        self.console_logger.log_new_connection(name,client_type)
        if client_type == "non-bot":
            await self.handle_client(websocket,name)
        else:
            await self.handle_bot(websocket,name)

    async def handle_type(self,websocket,name,client_type):
        try:
            if client_type in self.accepted_types:
                self.devices[name] = websocket
                self.devices_type[name] = client_type
                self.last_alert_sent[name] = datetime.datetime.now()

                await asyncio.wait_for(websocket.send("success"),10)
                await self.next_steps(client_type,name,websocket)
            else:
                await asyncio.wait_for(websocket.send("error_invalid_type"),10)
        except:
            traceback.print_exc()

    async def check_declaration(self,websocket , path):
        try:     
            if self.is_banned(str(websocket.remote_address[0])):
                return
            if await self.is_authed(websocket,self.regular_password):
                type_of_client = await asyncio.wait_for(websocket.recv(), 10)
                name_and_type = self.name_and_type(type_of_client)
                outside_name = await asyncio.wait_for(websocket.recv(),10)

                # Name and type exists/there is no client with this name
                if name_and_type != None and name_and_type[0] not in self.devices:
                    self.outside_names[name_and_type[0]] = outside_name
                    await self.handle_type(websocket,name_and_type[0],name_and_type[1]) 
                else:
                    self.console_logger.log_name_check_error(name_and_type[0])
                    await websocket.send("issue")
            else:
                
                await websocket.send("issue")    
        except Exception as e:
            traceback.print_exc()
            print(e)

    def is_banned(self,ip):
        if ip in self.failed_admin_attempts:
            if self.failed_admin_attempts[ip] > 3:
                print(f"the banned ip({ip}) is trying to auth")
                return True
            else:
                return False
        return False

    async def is_authed(self,websocket,specific_password):
        try:
            password = await asyncio.wait_for(websocket.recv(),35)
            if password == specific_password:
                return True
            else:
                self.add_to_failed_attempts(websocket)
                #re-check failed attempts after incrementing
                if self.is_banned(websocket.remote_address[0]):
                    raise AddressBannedException("Address is banned!!")
                return False
        except Exception as e:
            print("failed authentication from:" + str(websocket.remote_address[0]))
            #not timed out but banned 
            if e is AddressBannedException:
                raise e
            #timed out and banned
            if self.is_banned(websocket.remote_address[0]):
                raise AddressBannedException("Address is banned!!")
            #timed out and not banned
            self.add_to_failed_attempts(websocket)
            traceback.print_exc()
            return False

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

    def there_are_only_bots(self):
        names = self.devices.keys()
        for name in names:
            if self.devices_type[name] == "non-bot":
                return False
        return True

    async def check_for_alert(self,websocket,name):
        try:
            await asyncio.wait_for(websocket.send("alert"),5)
            result = await asyncio.wait_for(websocket.recv(),5)
            data_dict = json.loads(result)
            if data_dict["status"] == "alert_present":
                self.console_logger.log_generic_row(f"Sending Alert for {name}","red")
                self.twilio_handler.send_notification(data_dict["message"])
            self.available_status[name] = True
        except Exception as e:
            self.available_status[name] = True
            traceback.print_exc()

    #handles the extensive/advanced requests
    async def route_client_advanced_request(self,handler,request):
        if  "change_config_" in request:
            await handler.handle_config_request(request)
        else:
            pass

    def alert_will_not_be_spam(self,name):
        #30 seconds passed'
        now = datetime.datetime.now()
        if (now - self.last_alert_sent[name]).total_seconds() >= 30:
            self.last_alert_sent[name] = now
            return True
        else:
            return False

    async def try_to_gather_bot_passive_data(self,name,websocket):
        try:
            passive_data = await asyncio.wait_for(websocket.recv(),0.5)
            self.bot_passive_data[name] = passive_data
        except Exception as e:
            if e is websockets.exceptions.ConnectionClosed:
                raise e
            else:
                pass
            
    def banned_ips(self):
        ips = self.failed_admin_attempts.keys()
        banned_ips_holder = set()
        for ip in ips :
            if self.failed_admin_attempts[ip] > 3:
                banned_ips_holder.add(ip)
        return banned_ips_holder

    def start_server(self):
        self.console_logger.start_message()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            websockets.serve(self.check_declaration,self.host,self.port,ping_interval=None))
        loop.run_forever()

Main().start_server()
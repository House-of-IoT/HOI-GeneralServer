import asyncio
import json
import websockets
import datetime
from HybridActionsAndAutoScheduling.auto_scheduler import AutoScheduler
from Errors.errors import AddressBannedException
from client_handler import ClientHandler
from device_handler import DeviceHandler
from colorama import init
from console_logging import ConsoleLogger
from ThirdPartyHandlers.twilio_handler import TwilioHandler
from Config.config import ConfigHandler
from DataCapture.capture_and_serve_manager import CaptureAndServeManager
from DataObjects.type_handler import TypeHandler
from DataObjects.routing_types import RoutingTypes
from DataCapture.capture_object_creator import CaptureDictCreator
import queue
import traceback
import os

class Main:
    def __init__(self):
        init()#color for windows cli
        self.gather_env()
        self.set_basic_empty_state()
        self.device_handler = DeviceHandler(self)
        self.console_logger = ConsoleLogger(self)
        self.twilio_handler = TwilioHandler(self)
        self.config = ConfigHandler()
        self.auto_scheduler = AutoScheduler(5,self)
        self.type_handler = TypeHandler()
        self.capture_and_serve_manager = CaptureAndServeManager(self.config.using_sql,self)
        
    """
    Starting point for all new connections
    """
    async def check_declaration(self,websocket, path):
        try:     
            if self.is_banned(str(websocket.remote_address[0])):
                return
            if await self.is_authed(websocket,self.regular_password):
                type_of_client = await asyncio.wait_for(websocket.recv(), 10)
                name_and_type = self.name_and_type(type_of_client)
                outside_name = await asyncio.wait_for(websocket.recv(),10)
                await self.validate_name_and_type_and_continue(
                    name_and_type,
                    outside_name,
                    websocket)
            else:
                await websocket.send("issue")    
        except Exception as e:
            traceback.print_exc()

    """
    Waits on a request from the client and routes the request
    by using a ClientHandler instance.
    """
    async def handle_client(self,websocket,name):
        handler = ClientHandler(self,name,websocket)
        while True:
            await asyncio.sleep(1)
            try:
                await self.route_client_request(websocket,handler)
            except Exception as e:      
                del self.devices[name]
                del self.devices_type[name]
                self.console_logger.log_disconnect(name)
                traceback.print_exc()
                break      
    
    """
    Gathers passive data on a hard-coded interval if
    the bot isn't being used by a client.
    """
    async def handle_bot(self,websocket,name):
        self.available_status[name] = True
        self.gathering_passive_data[name] = False
        while True:
            try:
                if name not in self.devices:
                    break
                if self.available_status[name] == True and name not in self.deactivated_bots:
                    await self.try_to_gather_bot_passive_data(name,websocket)
                await asyncio.sleep(5.5)
            except Exception as e:
                #issue sending to websocket
                del self.devices[name]
                del self.devices_type[name]
                del self.bot_passive_data[name]
                self.console_logger.log_disconnect(name)
                traceback.print_exc()
                break

    """
    Does a validation check on the type claimed by the client
    and proceeds with next_steps if the type is valid.
    """
    async def handle_type(self,websocket,name,client_type):
        try:
            if self.type_handler.is_valid(client_type):
                self.devices[name] = websocket
                self.devices_type[name] = client_type
                self.last_alert_sent[name] = datetime.datetime.now()

                await asyncio.wait_for(websocket.send("success"),10)
                await self.next_steps(client_type,name,websocket)
            else:
                await asyncio.wait_for(websocket.send("error_invalid_type"),10)
        except:
            traceback.print_exc()

    """ 
    Returns true or false if passwords don't match
    and enforces network bans if too many failed attempts occured
    """
    async def is_authed(self,websocket,specific_password):
        try:
            password = await asyncio.wait_for(websocket.recv(),35)
            if password == specific_password:
                return True
            else:
                self.add_to_failed_attempts(websocket)
                ip = websocket.remote_address[0]
                #re-check failed attempts after incrementing
                if self.is_banned(ip):
                    banned_capture_data = CaptureDictCreator.create_banned_dict(ip,"add")
                    basic_capture_dict = CaptureDictCreator.create_basic_dict("banned",banned_capture_data)
                    await self.capture_and_serve_manager.try_to_route_and_capture(basic_capture_dict)
                    raise AddressBannedException("Address is banned!!")
                return False

        except Exception as e:
            self.handle_is_authed_exception(e,websocket)
            return False
    """
    Makes sure this person isn't already connected and their type is acceptable
    
    """
    async def validate_name_and_type_and_continue(self,name_and_type,outside_name,websocket):
        #Make sure the name doesn't exist already
        if name_and_type != None and name_and_type[0] not in self.devices:
            self.outside_names[name_and_type[0]] = outside_name
            await self.handle_type(websocket,name_and_type[0],name_and_type[1]) 
        else:
            self.console_logger.log_name_check_error(name_and_type[0])
            await websocket.send("issue")

    """
    Enter main loop for the specific type. Handle bots or non-bots.
    """
    async def next_steps(self,client_type, name,websocket):
        self.console_logger.log_new_connection(name,client_type)
        #try to capture the connection in memory or using the db
        connection_capture_data = CaptureDictCreator.create_connection_dict(name,client_type)
        basic_capture_dict = CaptureDictCreator.create_basic_dict("connection",connection_capture_data)
        await self.capture_and_serve_manager.try_to_route_and_capture(basic_capture_dict)
        #route to the main loop
        if client_type == "non-bot":
            await self.handle_client(websocket,name)
        else:
            await self.handle_bot(websocket,name)

    async def route_client_request(self,websocket,handler):
        request = await websocket.recv()
        if request == "bot_control":
            await handler.gather_request_for_bot()
        elif request == "servers_devices":
            await handler.send_table_state(self.devices_type,"servers_devices","both")
        elif request == "servers_deactivated_bots":
            await handler.send_table_state(self.deactivated_bots,"servers_deactivated_bots","values-set")
        elif request == "servers_banned_ips":
            await handler.send_table_state(None,"servers_banned_ips","values-set")
        elif request == "passive_data":
            await self.device_handler.get_and_send_passive_data(handler.name)
        else:
            await self.route_client_advanced_request(handler,request)   

    async def route_client_advanced_request(self,handler,request):
        if  "change_config_" in request or request in RoutingTypes.STATE_OR_RECORD_MODIFICATION:
            await handler.handle_state_or_record_modification(request)
        elif request in RoutingTypes.GENERIC_STATE_WITH_NO_AUTH:
            await handler.send_table_state_with_no_auth_requirements(request)
        else:
            pass

    async def try_to_gather_bot_passive_data(self,name,websocket):
        try:
            self.gathering_passive_data[name] = True
            await asyncio.wait_for(websocket.send("passive_data"),1)
            passive_data = await asyncio.wait_for(websocket.recv(),10.5)
            self.gathering_passive_data[name] = False
            await self.check_for_alert_and_send(passive_data,name)
            self.bot_passive_data[name] = passive_data
        except Exception as e:
            #Will close connection of bot and client
            traceback.print_exc()
            if e is websockets.exceptions:
                raise e
            elif e is not asyncio.TimeoutError:
                raise e
            else:
                pass

        self.gathering_passive_data[name] = False

    def is_banned(self,ip):
        if ip in self.failed_admin_attempts:
            if self.failed_admin_attempts[ip] > 3:
                print(f"the banned ip({ip}) is trying to auth")
                return True
            else:
                return False
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

    def name_and_type(self, response):
        try:
            data_dict = json.loads(response)
            if "name" in data_dict and "type" in data_dict:
                return (data_dict["name"] , data_dict["type"])
            else:
                return None
        except: 
            return None 

    async def check_for_alert_and_send(self,data,name):
        try:
            data_dict = json.loads(data)
            if data_dict["alert_status"] == "alert_present" and self.alert_will_not_be_spam(name):
                self.console_logger.log_generic_row(f"Sending Alert for {name}","red")
                self.twilio_handler.send_notifications_to_all(data_dict["message"])
        except:
            traceback.print_exc()

    def banned_ips(self):
        ips = self.failed_admin_attempts.keys()
        banned_ips_holder = set()
        for ip in ips :
            if self.failed_admin_attempts[ip] > 3:
                banned_ips_holder.add(ip)
        return banned_ips_holder

    def there_are_only_bots(self):
        names = self.devices.keys()
        for name in names:
            if self.devices_type[name] == "non-bot":
                return False
        return True

    def alert_will_not_be_spam(self,name):
        #30 seconds passed'
        now = datetime.datetime.now()
        if (now - self.last_alert_sent[name]).total_seconds() >= 30:
            self.last_alert_sent[name] = now
            return True
        else:
            return False

    def gather_env(self):
        self.admin_password = os.environ.get("apw_hoi_gs")
        self.regular_password = os.environ.get("rpw_hoi_gs")
        self.super_admin_password = os.environ.get("sapw_hoi_gs")

    def handle_is_authed_exception(self,e,websocket):
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

    def set_basic_empty_state(self):
        self.bot_passive_data = {}
        self.gathering_passive_data = {}
        self.contacts = {}
        self.most_recent_scheduled_tasks = {}
        self.most_recent_executed_actions = queue.Queue()
        self.most_recent_connections = queue.Queue()
        self.devices = {}
        self.devices_type = {}
        self.failed_admin_attempts = {}
        self.available_status = {}
        self.deactivated_bots = set()
        self.last_alert_sent = {}
        self.stream_mode_status= {}
        self.outside_names = {}
        self.alerts_enabled = True

    def start_server(self):
        self.console_logger.start_message()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            websockets.serve(self.check_declaration,self.config.host,self.config.port,ping_interval=None))
        loop.run_until_complete(
            self.auto_scheduler.execute_tasks())
        loop.run_forever()

if __name__ == "__main__":
    main = Main()
    main.start_server()
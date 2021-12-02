import asyncio
import json
from Errors.errors import AddressBannedException
from Errors.errors import BotStuckInPassiveDataGather
from Errors.errors import IssueGatheringServeData
from DataObjects.BasicResponse import BasicResponse
from AutoScheduling.auto_scheduler import Task
from SpecialActions.special_action_handler import SpecialActionHandler
from dateutil import parser
from DataObjects.routing_types import RoutingTypes
from DataCapture.capture_object_creator import CaptureDictCreator
from Response.response_manager import ResponseManager
from Actions.action_handler import ActionHandler
from Credentials.credential_checker import CredentialChecker
import traceback
import datetime
import queue

"""
Handles all bot requests and triggers actions
"""
class ClientHandler:
    def __init__(self,parent,name,websocket):
        self.parent = parent
        self.name = name
        self.websocket = websocket
        self.special_action_handler = SpecialActionHandler()
        self.response_manager = ResponseManager(websocket,parent,name)
        self.credential_checker = CredentialChecker(
            self.response_manager,
            parent,
            self.websocket)
        self.action_handler = ActionHandler(
            parent,
            websocket,
            self.response_manager,
            name,
            self.credential_checker)

#PUBLIC
    async def gather_request_for_bot(self):
        name_holder_for_error = None
        try:
            action = await  asyncio.wait_for(self.websocket.recv(),10)
            bot_name = await asyncio.wait_for(self.websocket.recv(),10)
            name_holder_for_error = bot_name

            if bot_name in self.parent.devices and self.parent.available_status[bot_name] == True:
                #establish control over the bot and wait until the passive data recv clear
                self.parent.available_status[bot_name] = False
                await self.wait_on_bot_passive_data_recv_to_clear(bot_name)
                await self.handle_action(bot_name,action)
            else:
                self.parent.console_logger.log_generic_row(
                    f"'{self.name}' has requested an action from a non existing bot ","red")

                await self.response_manager.send_basic_response("failure")

        except Exception as e:
            if name_holder_for_error in self.parent.available_status:
                self.parent.available_status[name_holder_for_error] = True
            await self.handle_bot_control_exception(e)
                
    async def send_table_state(self,table_or_set,target,keys_or_values_or_both):
        if(await self.credential_checker.client_has_credentials("viewing")):
            try:
                #if we get a null object we need to use the capture manager.
                if table_or_set == None:
                    table_or_set_capture_manager = await  self.parent.capture_and_serve_manager.try_to_gather_serve_target(target)
                    await self.route_data_request_and_send(
                        keys_or_values_or_both,
                        table_or_set_capture_manager,
                        target)
                else:
                    await self.route_data_request_and_send(
                        keys_or_values_or_both,
                        table_or_set,
                        target)
            except Exception as e:
                await self.handle_send_table_state_exception(e,target)
        else:
            await self.response_manager.send_basic_response("failed-auth",action= "viewing",target=target)

    async def send_table_state_with_no_auth_requirements(self,target):
        no_auth_types = RoutingTypes.GENERIC_STATE_WITH_NO_AUTH 
        no_auth_types_with_capture_manager = RoutingTypes.GENERIC_STATE_WITH_NO_AUTH_CAPTURE_MANAGER

        try:
            #the requests that don't require auth or capture manager
            if target in no_auth_types and  target not in no_auth_types_with_capture_manager:
                table_state = self.route_no_auth_target_to_object(target)
                self.try_to_convert_dates(table_state)
                await self.send_generic_table_state(
                    "viewing",
                    target,
                    table_state)

            elif target in RoutingTypes.GENERIC_STATE_WITH_NO_AUTH_CAPTURE_MANAGER:
                table_state = await self.parent.capture_and_serve_manager.try_to_gather_serve_target(target)
                self.try_to_convert_dates(table_state)
                await self.send_generic_table_state(
                    "viewing",
                    target,json.dumps(table_state))
                
        except Exception as e:
            print(e)
            await self.handle_send_table_state_exception(e,target)

    async def handle_state_or_record_modification(self,target):
        #gather the correct function and whether or not is is a coroutine
        lambda_and_async_status = self.route_modification_target_to_lambda(target)

        #pass the correct function and handle it as a super auth request
        await self.handle_super_auth_request(
            target,
            "editing",
            lambda_and_async_status[0],
            is_async=lambda_and_async_status[1])
#PRIVATE
    """
    Takes action and routes it to the correct functionality
    """
    async def handle_action(self,bot_name,action):
        bot_type = self.parent.devices_type[bot_name]
        await self.check_and_wait_if_gathering_passive_data(bot_name)
        if action == "activate" or action == "deactivate" or action == "disconnect":
            await self.action_handler.activate_deactivate_or_disconnect_bot(bot_name,action)
        else:
            if bot_name in self.parent.deactivated_bots:
                await asyncio.wait_for(self.websocket.send("issue"),10)
                return
            await self.check_bot_capabilities_and_finish_action(action,bot_name)
            self.action_handler.set_bot_back_to_available(bot_name)

        #capture the action execution
        action_capture_data = CaptureDictCreator.create_action_dict(
            self.name,bot_name,action,bot_type)
        basic_capture_dict = CaptureDictCreator.create_basic_dict("executed_action",action_capture_data)
        await self.parent.capture_and_serve_manager.try_to_route_and_capture(basic_capture_dict)

    """
    1. Gather value for the request from client
    2. Gather authentication credentials from client
    3. Execute passed in function(correct function for the request) if client is 
       successfully authenticated.
    """
    async def handle_super_auth_request(self,request,action,fun,is_async=True):
        try:
            status = None
            value = await asyncio.wait_for(self.websocket.recv(),40)
            successfully_authed_with_super_pass = await self.credential_checker.send_need_admin_auth_and_check_response(
                self.parent.super_admin_password,"editing")

            if successfully_authed_with_super_pass:
                if is_async:
                    await fun(request,value)
                else:
                    fun(request,value)
                status = "success"
            else:
                status = "failure"
            await self.response_manager.send_basic_response(status,action=action,target=request)
        except Exception as e:
            await self.handle_super_auth_request_exception(e,request)

    async def send_generic_table_state(self,action,target,value):
        try:
            await self.response_manager.send_basic_response(
                "success",
                action= action,
                target=target ,
                target_value=value)
        except Exception as e:
            print(e)
            self.parent.console_logger.log_generic_row(f"A request that {self.name} made has timed out!","red")
            await self.response_manager.send_basic_response("timeout", action= action,target=target)

    async def check_bot_capabilities_and_finish_action(self,action,bot_name):
        if self.bot_type_has_capability(bot_name,action) and action in RoutingTypes.BASIC_ACTIONS:
            await self.action_handler.execute_basic_action_protocol(bot_name,action)
        elif self.bot_type_has_capability(bot_name,action):
            await asyncio.wait_for(self.websocket.send("success"),10)
            await self.special_action_handler.execute_special_action(
                action,
                self.parent.devices[bot_name],
                self.websocket)
        else:
            await asyncio.wait_for(self.websocket.send("issue"),10) 

    def bot_type_has_capability(self,bot_name,action):
        try:
            device_type = self.parent.devices_type[bot_name]
            capabilties = self.parent.type_handler.accepted_types[device_type]
            return capabilties.functionality[action]
        except:
            traceback.print_exc()
            return False

    #convert config to having db capture?
    def modify_matching_config_boolean(self,request,new_value):
        boolean = bool(int(new_value))
        if request == "change_config_viewing":
            self.parent.config.viewing_all_devices_requires_auth = boolean
        elif request == "change_config_activating":
            self.parent.config.activating_requires_admin = boolean
        elif request == "change_config_deactivating":
            self.parent.config.deactivating_requires_admin = boolean
        else:
            self.parent.config.disconnecting_requires_admin = boolean

    async def add_or_remove_contact(self,request,new_value):

        name_and_number = json.loads(new_value)
        name = name_and_number["name"]
        number = name_and_number["number"]
        contact_capture_data = CaptureDictCreator.create_contact_dict(name,number,request)
        basic_capture_dict =  CaptureDictCreator.create_basic_dict("contact",contact_capture_data)
        await self.parent.capture_and_serve_manager.try_to_route_and_capture(basic_capture_dict)
        self.parent.console_logger.log_generic_row(f"Successfully attempted {request} on {name}({number})!", "green")

    def add_or_remove_task(self,request,value):
        data_dict = json.loads(value)
        str_to_datetime = parser.parse(data_dict["time"])

        name = data_dict["name"]
        action = data_dict["action"]
        reoccuring = data_dict["reoccuring"]

        task = Task(str_to_datetime,name,action,reoccuring)
        if request == "add-task":
            self.parent.auto_scheduler.add_task(task)
        else:
            self.parent.auto_scheduler.cancel_task(task)
    
    async def add_or_remove_banned_ip(self,request,value):
        ip = value
        capture_banned_data = CaptureDictCreator.create_banned_dict(ip,request)
        basic_capture_dict = CaptureDictCreator.create_basic_dict("banned",capture_banned_data)
        await self.parent.capture_and_serve_manager.try_to_route_and_capture(basic_capture_dict)

    """
    Takes an object and gets the requested attributes from it 
    and sends them in basic response format.

    keys -> Gets the keys of a dict(list)
    values -> Gets the values of a dict(list)
    values-set -> Gets the values of a set(list)
    both(else) -> Just returns the full dict(json serialized dict -> str)
    """
    async def route_data_request_and_send(self,keys_or_values_or_both,table_or_set,target):
        target_value = None
        if keys_or_values_or_both == "keys":
            target_value = table_or_set.keys()
        elif keys_or_values_or_both == "values":
            target_value = table_or_set.values()
        elif keys_or_values_or_both == "values-set":
            target_value = list(table_or_set)
        else:
            target_value = json.dumps(table_or_set)
        await self.response_manager.send_basic_response(
            "success",
            action = "viewing", 
            target = target, 
            target_value = target_value)

    async def check_and_wait_if_gathering_passive_data(self,name):
        while self.parent.gathering_passive_data[name] == True:
            await asyncio.sleep(1)

    async def wait_on_bot_passive_data_recv_to_clear(self,name):
        start_time = datetime.datetime.utcnow()
        while True:
            await asyncio.sleep(0.5)
            if self.parent.gathering_passive_data[name] == False:
                break
            current_time = datetime.datetime.utcnow()
            seconds_passed = (current_time-start_time).total_seconds()
            if seconds_passed > 12 and self.parent.gathering_passive_data[name]:
                raise BotStuckInPassiveDataGather("Bot stuck in passive data gather.")

    def route_no_auth_target_to_object(self,target):
        if target == "server_config":
            return self.parent.config.string_version()
        elif target == "task_list":
            target_copy = self.parent.auto_scheduler.tasks_to_dict().copy()
            self.try_to_convert_dates(target_copy)
            return json.dumps(target_copy)
        elif target == "recent_executed_tasks":
            #create copy of queue and covert the original queue into a list.
            #overwrite the old queue variable
            old_queue = self.parent.most_recent_executed_tasks
            queue_and_list = self.convert_queue_to_list_and_create_queue_copy(old_queue)
            self.parent.most_recent_executed_tasks = queue_and_list[0]
            tasks = self.convert_all_tasks_to_dict(queue_and_list[1])
            return json.dumps(tasks)

    async def handle_bot_control_exception(self,e):
        traceback.print_exc()
        if e is AddressBannedException:
            ip = self.websocket.remote_address[0]
            self.parent.console_logger.log_generic_row(f"{self.name} or ({ip}) is now banned!!","red" )
            raise e
        if e is BotStuckInPassiveDataGather:
            await self.websocket.send("fatal_timeout")
        else:
            await self.websocket.send("timeout")

    def convert_queue_to_list_and_create_queue_copy(self,old_queue):
        new_queue = queue.Queue()
        new_list = []

        while old_queue.qsize()>0:
            queue_value = old_queue.get()
            new_queue.put(queue_value)
            new_list.append(queue_value)

        return (new_queue,new_list)

    def convert_all_tasks_to_dict(self,tasks):
        new_tasks = []
        for task in tasks:
            new_tasks.append(task.task_to_dict())
        return new_tasks

    async def handle_send_table_state_exception(self,e,target):
        traceback.print_exc()
        if e is IssueGatheringServeData:
            await self.response_manager.send_basic_response(
                "fatal_gathering",
                action= "viewing",
                target=target)
        else:
            await self.response_manager.send_basic_response(
                "timeout",
                action= "viewing",
                target=target)

    async def handle_super_auth_request_exception(self,e,request):
        traceback.print_exc()
        if e is AddressBannedException:
            raise e
        else:   
            traceback.print_exc()
            self.parent.console_logger.log_generic_row(f"A request that {self.name} made has timed out!","red")
            await self.response_manager.send_basic_response("timeout",action= "editing", target=request)

    """
    returns the correct lambda for a target modification
    and whether or not the lambda is a coroutine.
    """
    def route_modification_target_to_lambda(self,target):
        if target == "add-banned-ip" or target == "remove-banned-ip":
            return (lambda x,y:self.add_or_remove_banned_ip(x,y),True)
        elif target == "add-task" or target == "remove-task":
            return (lambda x,y: self.add_or_remove_task(x,y),False)
        elif "change_config_" in target:
            return (lambda x,y: self.modify_matching_config_boolean(x,y),False)
        else:
            return (lambda x,y: self.add_or_remove_contact(x,y),True)

    def convert_dates_to_str_list(self,data):
        try:
            for dict_obj in data:
                if "date" in dict_obj:
                    dict_obj["date"] = str(dict_obj["date"])
        except:
            pass

    def convert_dates_to_str_dict(self,data):
        try:
            if "date" in data:
                data["date"] = str(data["date"])
        except:
            pass
    """
    Converts dates to str since the datetime object can't be serialized(json)
    correctly with the json lib.
    """
    def try_to_convert_dates(self,data):
        self.convert_dates_to_str_list(data)
        self.convert_dates_to_str_dict(data)
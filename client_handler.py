import asyncio
import json
from errors import AddressBannedException
from BasicResponse import BasicResponse
import traceback

class ClientHandler:
    def __init__(self,parent,name,websocket):
        self.parent = parent
        self.name = name
        self.websocket = websocket

#PUBLIC
    async def gather_request_for_bot(self):
        try:
            action = await  asyncio.wait_for( self.websocket.recv(),10)
            bot_name = await asyncio.wait_for(  self.websocket.recv(),10)

            if bot_name in self.parent.devices and self.parent.available_status[bot_name] == True:
                await self.handle_action(bot_name,action)
            else:
                empty_response = BasicResponse(self.parent.outside_names[self.name]).string_version()
                self.parent.console_logger.log_generic_row(f"'{self.name}' has requested an action from a non existing bot ","red")
                await asyncio.wait_for(self.websocket.send(empty_response),10)

        except Exception as e:
            traceback.print_exc()
            if e is AddressBannedException:
                ip = self.websocket.remote_address[0]
                self.parent.console_logger.log_generic_row(f"{self.name} or ({ip}) is now banned!!","red" )
                raise e
            else:
                await self.websocket.send("timeout")
                
    #sending the server's live table state
    async def send_table_state(self,table_or_set,target,keys_or_values_or_both):
        if(await self.client_has_credentials("viewing")):
            try:
                target_value = None
                if keys_or_values_or_both == "keys":
                    target_value = table_or_set.keys()
                elif keys_or_values_or_both == "values":
                    target_value = table_or_set.values()
                elif keys_or_values_or_both == "values-set":
                    target_value = list(table_or_set)
                else:
                     target_value = json.dumps(table_or_set)
                await self.send_basic_response("success",action = "viewing", target= target, target_value= target_value)
            except Exception as e:
                print(e)
                await self.send_basic_response("timeout",action= "viewing",target=target)
        else:
            await self.send_basic_response("failed-auth",action= "viewing",target=target)

    async def send_server_config(self):
        try:
            await self.send_basic_response(
                "success",
                action= "viewing",
                target="server_config" ,
                target_value=self.parent.config.string_version())
        except Exception as e:
            print(e)
            self.parent.console_logger.log_generic_row(f"A request that {self.name} made has timed out!","red")
            await self.send_basic_response("timeout", action= "viewing",target="server_config")
            
    #editing the server's live config settings
    async def handle_config_request(self,request):
        status = None
        try:
            new_boolean = bool(await asyncio.wait_for(self.websocket.recv(),40))      
            successfully_authed_with_super_pass = self.send_need_admin_auth_and_check_response(self.parent.super_admin_password,"editing")

            if successfully_authed_with_super_pass:
                self.modify_matching_config_boolean(request,new_boolean)
                status = "success"
            else:
                status = "failure"
            await self.send_basic_response(status,action="editing",target=request)

        except Exception as e:
            traceback.print_exc()
            if e is AddressBannedException:
                raise e
            else:   
                traceback.print_exc()
                self.parent.console_logger.log_generic_row(f"A request that {self.name} made has timed out!","red")
                await self.send_basic_response("timeout",action= "editing", target=request)
#PRIVATE
    async def check_for_stop(self,bot_name):
        try:
            message = asyncio.wait_for(self.websocket.recv() , 0.1)
            if message == "finished_streaming":
                self.stream_mode_status[self.name] = False
                self.available_status[bot_name] = True
                await self.devices[bot_name].send("stop_streaming")
                return True
            else:
                return False
        except:
            pass

    async def begin_capability(self,bot_name,action):
        if action == "video_stream" or action == "audio_steam" and  self.parent.available_status[bot_name] == True :
            self.parent.available_status[bot_name] = False
            self.parent.stream_mode_status[self.name] = True
            await self.stream(bot_name,action)

    async def activate_deactivate_or_disconnect_bot(self,bot_name,action):
        if(await self.client_has_credentials(action)):
            #send bot the basic request
            bot_connection  = self.parent.devices[bot_name]
            await asyncio.wait_for(bot_connection.send(action),10)
            status = await asyncio.wait_for(bot_connection.recv(),10);
            self.parent.console_logger.log_generic_row(f"bot({bot_name}) responded with {status} to {self.name}'s action request:{action}\n","green")
            #send client the result
            await self.send_basic_response(status,action= action,bot_name=bot_name)
            self.handle_activate_deactivate_or_disconnect_cleanup(bot_name,action,status)
        else:
            await self.send_basic_response("failure",action= action,bot_name=bot_name)
        
    def handle_activate_deactivate_or_disconnect_cleanup(self,bot_name,action,status):
        if status == "success":
            if action == "activate":
                self.parent.deactivated_bots.remove(bot_name)
            elif action == "deactivate":
                self.parent.deactivated_bots.add(bot_name)
            else:
                del self.parent.devices[bot_name]
                del self.parent.outside_names[bot_name]
                del self.parent.devices_type[bot_name]
                if bot_name in self.parent.deactivated_bots:
                    self.parent.deactivated_bots.remove(bot_name)
                if bot_name in self.parent.stream_mode_status:
                    del self.parent.stream_mode_status[bot_name]
                self.parent.console_logger.log_disconnect(bot_name)
                    
    async def stream (self,bot_name,action):
        if await self.bot_was_notified(bot_name,action):
            while  self.parent.stream_mode_status[self.name] == True:
                try:
                    if await self.check_for_stop() == True:
                        break    
                    await self.gather_data_from_bot_and_forward(bot_name)

                except:
                    traceback.print_exc()
                    self.stream_mode_status[self.name] = False
                    self.available_status[bot_name] = True
                await asyncio.sleep(0.1)
        
        self.stream_mode_status[self.name] = False
        self.available_status[bot_name] = True

    async def gather_data_from_bot_and_forward(self,bot_name):
        bot_websocket = self.parent.devices[bot_name]
        data = await asyncio.wait_for(bot_websocket.recv(),10)
        await asyncio.wait_for(self.websocket.send(data),10)

    async def bot_was_notified(self,bot_name,action)-> bool:
        try:
            bot_websocket = self.parent.devices[bot_name]
            await asyncio.wait_for(bot_websocket.send(action),10)
            response = await asyncio.wait_for(bot_websocket.recv(),10)
            if response == "got_request":
                return True
            else:
                return False
        except:
            return False

    async def handle_action(self,bot_name,action):
        if action == "activate" or action == "deactivate" or action == "disconnect":
            await self.activate_deactivate_or_disconnect_bot(bot_name,action)

        elif self.bot_type_has_capability(bot_name,action):
            if bot_name in self.parent.deactivated_bots:
                await asyncio.wait_for(self.websocket.send("bot is deactivated!!"),10)
                return
            await asyncio.wait_for(self.websocket.send("success"),10)
            self.begin_capability(bot_name,action)

        else:
            await asyncio.wait_for(self.websocket.send("issue"),10)

    def bot_type_has_capability(self,bot_name,action)-> bool:
        try:
            device_type = self.parent.devices_type[bot_name]
            capabilties = self.accepted_types[device_type]
            return capabilties.functionality[action]
        except:
            traceback.print_exc()
            return False

    async def gather_deactivated_bots(self):
        bots = list(self.parent.deactivated_bots)
        return json.dumps(bots)

    #Checks if an action requires admin auth and prompts for auth if needed.
    async def client_has_credentials(self,action):
        config_bool = self.route_action_to_config_bool(action)
        if config_bool:
            return await self.send_need_admin_auth_and_check_response(self.parent.admin_password,action)
        else:
            return True
    
    #returns the truth status for an action needing admin auth.
    def route_action_to_config_bool(self, action):
        if action == "activate":
            return self.parent.config.activating_requires_admin
        elif action == "deactivate":
            return self.parent.config.deactivating_requires_admin
        elif action == "disconnect":
            return self.parent.config.disconnecting_requires_admin
        elif action == "viewing":
            return self.parent.config.viewing_all_devices_requires_auth
        else:
            return True

    async def modify_matching_config_boolean(self,request,new_boolean):
        if request == "change_config_viewing":
            self.parent.config.viewing_all_devices_requires_auth = new_boolean
        elif request == "change_config_activating":
            self.parent.config.activating_requires_admin = new_boolean
        elif request == "change_config_deactivating":
            self.parent.config.deactivating_requires_admin = new_boolean
        else:
            self.parent.config.disconnecting_requires_admin = new_boolean

    async def send_need_admin_auth_and_check_response(self,password,action):
        await self.send_basic_response("needs-admin-auth",action = action)
        if await self.parent.is_authed(self.websocket,password):
            return True
        else:
            return False

    async def send_basic_response(
        self,status,action = None,
        target = None,target_value = None ,bot_name = None):
        basic_response = BasicResponse(self.parent.outside_names[self.name])
        basic_response.action = action
        basic_response.status = status
        basic_response.bot_name = bot_name
        basic_response.target = target
        basic_response.target_value = target_value
        await asyncio.wait_for(self.websocket.send(basic_response.string_version()),40)

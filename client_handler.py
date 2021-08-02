import asyncio
import json
from errors import AddressBannedException
from BasicResponse import BasicResponse

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
            if e is AddressBannedException:
                raise e
            else:
                await self.websocket.send("timeout")
                print(e)

    async def send_table_state(self,table_or_set,target,keys_or_values_or_both):
        state_response = BasicResponse(self.parent.outside_names[self.name])
        state_response.target = target
        state_response.action = "viewing"
        if(await self.client_has_credentials("viewing")):
            try:
                state_response.status = "success"
                if keys_or_values_or_both == "keys":
                    state_response.target_value = table_or_set.keys()
                elif keys_or_values_or_both == "values":
                    state_response.target_value = table_or_set.values()
                elif keys_or_values_or_both == "values-set":
                    state_response.target_value = list(table_or_set)
                else:
                     state_response.target_value = json.dumps(table_or_set)
                await asyncio.wait_for(self.websocket.send(state_response.string_version()),10)
            except Exception as e:
                print(e)
                await self.notify_timeout(state_response)
        else:
            state_response.status = "failed-auth"
            await asyncio.wait_for(self.websocket.send(state_response.string_version()),40)

    async def handle_config_request(self,request):
        if self.parent.is_authed

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
        server_name = self.parent.outside_names[self.name]
        basic_response = BasicResponse(server_name)
        basic_response.action = action
        basic_response.bot_name = bot_name
        try:
            if(await self.client_has_credentials(action)):
                #send bot the basic request
                bot_connection  = self.parent.devices[bot_name]
                await asyncio.wait_for(bot_connection.send(action),10)
                status = await asyncio.wait_for(bot_connection.recv(),10);
                self.parent.console_logger.log_generic_row(f"bot({bot_name}) responded with {status} to {self.name}'s action request:{action}\n","green")
                basic_response.status = status
                #send client the result
                await asyncio.wait_for(self.websocket.send(basic_response.string_version()),10)
                self.handle_activate_deactivate_or_disconnect_cleanup(bot_name,action,status)
            else:
                basic_response.status = "Failed Auth"
                await asyncio.wait_for(self.websocket.send(basic_response.string_version()),10)
        except Exception as e:
            print(e)
            await self.notify_timeout(basic_response)
        
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
            return False

    async def gather_deactivated_bots(self):
        bots = list(self.parent.deactivated_bots)
        return json.dumps(bots)

    #Checks if an action requires admin auth and prompts for auth if needed.
    async def client_has_credentials(self,action):
        config_bool = self.route_action_to_config_bool(action)
        if config_bool:
            basic_response = BasicResponse(self.parent.outside_names[self.name])
            basic_response.action = action
            basic_response.status = "needs-admin-auth"
            await asyncio.wait_for(self.websocket.send(basic_response.string_version()),40)
            if await self.parent.is_authed(self.websocket,self.parent.admin_password):
                return True
            else:
                return False
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

    async def send_need_admin_auth(self):
        basic_response = BasicResponse(self.parent.outside_names[self.name])
        basic_response.action = action
        basic_response.status = "needs-admin-auth"
        await asyncio.wait_for(self.websocket.send(basic_response.string_version()),40)
        
    #on failure , the outer block will close the connection for notifies
    async def notify_timeout(self,response):
        response.status = "timeout"
        self.parent.console_logger.log_generic_row(f"A request that {self.name} made has timed out!","red")
        await asyncio.wait_for(self.websocket.send(response.string_version()),10)
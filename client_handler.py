
import asyncio

import websockets
from device_handler import DeviceHandler
from BasicResponse import BasicResponse

class ClientHandler:
    def __init__(self,parent,name,websocket):
        self.parent = parent
        self.name = name
        self.websocket = websocket

    async def gather_request_for_bot(self):
        try:
            action = await  asyncio.wait_for( self.websocket.recv(),1)
            bot_name = await asyncio.wait_for( await self.websocket.recv(),1)

            if bot_name in self.parent.devices and self.parent.available_status[bot_name] == True:
                if action == "activate" or action == "deactivate" or action == "disconnect":
                    self.activate_deactivate_or_disconnect_bot(bot_name,action)

                elif self.bot_type_has_capability(bot_name,action):
                    if bot_name in self.parent.deactivated_bots:
                        self.websocket.send("bot is deactivated!!")
                        return
                    await self.websocket.send("success")
                    self.begin_capability(bot_name,action)

                else:
                    await self.websocket.send("issue")

            else:
                await self.websocket.send("no bot by this name")

        except:
            pass

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
        try:
            server_name = self.parent.outside_names[self.name]
            #basic response setup
            basic_response = BasicResponse(server_name)
            basic_response.action = action
            basic_response.bot_name = bot_name
            #send bot the basic request
            bot_connection  = self.parent.devices[bot_name]
            await bot_connection.send(action)
            status = await asyncio.wait_for(bot_connection.recv(),1);
            basic_response.status = status
            #send client the result
            await self.websocket.send(basic_response.string_version())
            self.handle_activate_deactivate_or_disconnect_cleanup(bot_name,action,status)
        except:
            pass
        
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
                    del self.parent.deactivated_bots.remove(bot_name)
                if bot_name in self.parent.stream_mode_status:
                    del self.parent.stream_mode_status[bot_name]
                    
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
        data = await bot_websocket.recv()
        await self.websocket.send(data)

    async def  bot_was_notified(self,bot_name,action)-> bool:
        try:
            bot_websocket = self.parent.devices[bot_name]
            await bot_websocket.send(action)
            response = await bot_websocket.recv()
            if response == "got_request":
                return True
            else:
                return False
        except:
            return False

    def bot_type_has_capability(self,bot_name,action)-> bool:
        try:
            device_type = self.parent.devices_type[bot_name]
            capabilties = self.accepted_types[device_type]
            return capabilties.functionality[action]
        except:
            return False
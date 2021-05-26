
import asyncio
from device_handler import DeviceHandler

class ClientHandler:
    def __init__(self,parent,name,websocket):
        self.parent = parent
        self.name = name
        self.websocket = websocket

    async def gather_request(self):
        try:
            action = asyncio.wait_for( self.websocket.recv(),1)
            bot_name = asyncio.wait_for( await self.websocket.recv(),1)

            if bot_name in self.parent.devices:
                if self.bot_type_has_capability(bot_name,action):
                    await self.websocket.send("success")
                    self.begin_capability(bot_name,action)
                else:
                    await self.websocket.send("issue")
            else:
                await self.websocket.send("issue")

        except:
            pass

    def begin_capability(self,bot_name,action):
        if action == "video_stream" or action == "audio_steam" and  self.parent.available_status[bot_name] == True :
            self.parent.available_status[bot_name] = False
            self.parent.stream_mode_status[self.name] = True
            self.stream(bot_name)
            
    async def stream (self,bot_name):
        while  self.parent.stream_mode_status[self.name] == True:
            try:
                 # bot data exists
                if bot_name in self.parent.stream_data and len(self.parent.stream_data[bot_name]) > 0:
                    data = self.parent.stream_data[bot_name].pop(0)
                    await self.websocket.send(data)
                else:
                    pass
            except:
                self.stream_mode_status[self.name] = False
                self.available_status[bot_name] = True
                    

    def bot_type_has_capability(self,bot_name,action)-> bool:
        try:
            device_type = self.parent.devices_type[bot_name]
            capabilties = self.accepted_types[device_type]
            return capabilties.functionality[action]
        except:
            return False

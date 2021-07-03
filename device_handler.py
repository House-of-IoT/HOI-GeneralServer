import asyncio
import json

"""
Handles all data gathering/requesting from client to bot
"""

class DeviceHandler:    
    def __init__(self,parent):
        self.parent = parent

    #PUBLIC
    async def get_and_send_passive_data(self,client_name):
        device_names = self.parent.devices.keys()
        data_holder = {"server_name":self.parent.outside_names[client_name],"bots":[]}

        for name in device_names:
            if self.parent.devices_type[name] != "non-bot":
                bot_websocket = self.parent.devices[name]
                await self.try_to_gather_data_from_bot(bot_websocket,name,data_holder)
            else:
                pass
        await self.send_passive_data_to_client(data_holder,client_name)

    #PRIVATE
    async def send_passive_data_to_client(self ,data_holder,name):
        json_string = json.dumps(data_holder)
        try:
            await self.parent.devices[name].send(json_string)
        except:
            del self.parent.devices[name]

    async def try_to_gather_data_from_bot(self,websocket,name,data_holder):
        try:
            await asyncio.wait_for( websocket.send("basic_data") , 0.4)
            data = await asyncio.wait_for(websocket.recv(), 0.4)
            json_to_dict = json.loads(data)
            json_to_dict["type"] = self.parent.devices_type[name]
            data_holder["bots"].append(json_to_dict)
        except Exception  as e:
            print(e)
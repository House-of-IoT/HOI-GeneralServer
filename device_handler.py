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
        device_names = self.parent.bot_passive_data.keys()
        data_holder = {"server_name":self.parent.outside_names[client_name],"bots":[]}

        for name in device_names:
            if self.parent.available_status[name] == True:
                self.gather_bot_data(name,data_holder)
            else:
                pass
        await self.send_passive_data_to_client(data_holder,client_name)

    #PRIVATE
    async def send_passive_data_to_client(self ,data_holder,name):
        json_string = json.dumps(data_holder)
        try:
            await asyncio.wait_for(self.parent.devices[name].send(json_string),10)
        except Exception as e:
            raise e
            
    async def gather_bot_data(self,name,data_holder):
        try:
            data = self.parent.bot_passive_data[name]
            json_to_dict = json.loads(data)
            json_to_dict["active_status"] = name not in self.parent.deactivated_bots #false if the name is in the set
            json_to_dict["device_name"] = name
            json_to_dict["type"] = self.parent.devices_type[name]
            data_holder["bots"].append(json_to_dict)
        except Exception  as e:
            print(e)
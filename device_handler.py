import asyncio
import json

"""
gathers passive data from memory and sends to client
"""

class DeviceHandler:    
    def __init__(self,parent):
        self.parent = parent

    #PUBLIC
    async def get_and_send_passive_data(self,client_name):
        device_names = self.parent.bot_passive_data.keys()
        notifications = self.parent.notification_handler.serve_notifications(client_name)
        connected_clients_num = len(self.parent.outside_names.keys())
        deactivated_bots_num = len(self.parent.deactivated_bots)
        failed_num = len(self.parent.failed_auth_attempts.keys())
        device_amount = len(self.parent.devices_type.keys())
        passive_amount = len(self.parent.bot_passive_data.keys())
        data_holder = {
            "server_name":self.parent.outside_names[client_name],
            "bots":[], 
            "notifications":notifications,
            "type_op_codes":self.parent.type_handler.type_op_codes(),
            "server_state_lens":{
                "clients":connected_clients_num,
                "deactivated":deactivated_bots_num,
                "addresses_that_failed":failed_num,
                "devices":device_amount,
                "alerts_active":True,
                "in_memory_passive_data":passive_amount},
            "external_controller_snapshot":self.parent.external_controller_view_snapshot}

        for name in device_names:
            if self.parent.available_status[name] == True:
                await self.gather_bot_data(name,data_holder)
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
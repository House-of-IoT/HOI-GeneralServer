import asyncio
import json

class DeviceHandler:
    
    def __init__(self,parent):
        self.parent = parent

    async def send_passive_data(self,client_websocket ,data_holder,client_name):
        json_string = json.dumps(data_holder)
        try:
            await client_websocket.send(json_string)
        except:
            del self.parent.clients[client_name]

    async def try_to_gather_data_from_bot(self,websocket,name,data_holder):
        try:
            await asyncio.wait_for( websocket.send("basic_data") , 0.4)
            data = await asyncio.wait_for(websocket.recv(), 0.4)
            data_holder[name] = data
        except:
            pass

    #gathers bot devices status and sends to the connected non-bot
    async def get_and_send_passive_data(self,client_websocket,client_name):
        client_names = self.parent.clients.keys()
        data_holder = {}

        for name in client_names:
            if self.clients_type[name] != "non-bot":
                bot_websocket = self.clients[name]
                self.try_to_gather_data_from_bot(bot_websocket,name,data_holder)
            else:
                pass
        await self.send_passive_data(client_websocket,data_holder,client_name)



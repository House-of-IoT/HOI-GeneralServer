import asyncio 
from DataObjects.BasicResponse import BasicResponse

class ResponseManager:
    def __init__(self,websocket,parent,name):
        self.websocket = websocket
        self.parent = parent
        self.name = name
        
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
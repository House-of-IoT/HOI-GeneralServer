import asyncio
import BasicResponse

''' Used for composition of client handler and auto scheduler'''

class ActionUtils:    
    def __init__(self,websocket,name):
        self.websocket = websocket
        self.name = name

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

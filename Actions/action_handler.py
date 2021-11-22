
import asyncio

"""
Controls all of the basic action execution.

"parent" in this context is the Main object singleton 
even though this class is intended to be apart of the
ClientHandler composition
"""
class ActionHandler:
    def __init__(self,parent,websocket,response_manager,name,credential_checker):
        self.parent = parent
        self.websocket = websocket
        self.response_manager = response_manager
        self.name = name
        self.credential_checker = credential_checker

    """
    Takes actions that are "basic"(needs a one time opcode to change a device's state)
    and executes.
    """
    async def execute_basic_action_protocol(self,bot_name,action):
        if await self.credential_checker.client_has_credentials(action):
            #send bot the basic request
            bot_connection  = self.parent.devices[bot_name]
            await asyncio.wait_for(bot_connection.send(action),10)
            status = await asyncio.wait_for(bot_connection.recv(),10);
            self.parent.console_logger.log_generic_row(
                f"bot({bot_name}) responded with {status} to {self.name}'s action request:{action}\n","green")
            #send client the result
            await self.response_manager.send_basic_response(status,action= action,bot_name=bot_name)
            return (status,True)
        else:
            await self.response_manager.send_basic_response("failure",action= action,bot_name=bot_name)
            return (None,False)

    async def activate_deactivate_or_disconnect_bot(self,bot_name,action):
        credential_status_and_bot_return_status = await self.execute_basic_action_protocol(bot_name,action)
        bot_return_status = credential_status_and_bot_return_status[0]
        if bot_return_status == "success":
            self.handle_activate_deactivate_or_disconnect_cleanup(bot_name,action)
        
    def handle_activate_deactivate_or_disconnect_cleanup(self,bot_name,action):
        if action == "activate":
            self.parent.deactivated_bots.remove(bot_name)
            self.set_bot_back_to_available(bot_name)
        elif action == "deactivate":
            self.parent.deactivated_bots.add(bot_name)
            self.set_bot_back_to_available(bot_name)
            if bot_name in self.parent.bot_passive_data:
                del self.parent.bot_passive_data[bot_name]
        else:
            del self.parent.devices[bot_name]
            del self.parent.outside_names[bot_name]
            del self.parent.devices_type[bot_name]
            if bot_name in self.parent.bot_passive_data:
                del self.parent.bot_passive_data[bot_name]
            if bot_name in self.parent.deactivated_bots:
                self.parent.deactivated_bots.remove(bot_name)
            if bot_name in self.parent.stream_mode_status:
                del self.parent.stream_mode_status[bot_name]
            self.parent.console_logger.log_disconnect(bot_name)

    def set_bot_back_to_available(self,bot_name):
        if bot_name in self.parent.available_status:
            self.parent.available_status[bot_name] = True
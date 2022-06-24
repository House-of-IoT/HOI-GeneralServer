
"""This class is responsible for gathering authentication credentials for events
    that require authentication. Apart of the ClientHander's composition.

    parent is the Main object singleton.
"""
class CredentialChecker:
    def __init__ (self,response_manager,parent,websocket):
        self.response_manager = response_manager
        self.parent = parent
        self.websocket = websocket

    #Checks if an action requires admin auth and prompts for auth if needed.
    async def client_has_credentials(self,action):
        config_bool = self.route_action_to_config_bool(action)
        if config_bool:
            return await self.send_need_admin_auth_and_check_response(self.parent.admin_password,action)
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
        elif action == "editing_relations":
            return self.parent.config.relations_editing_requires_admin_auth
        else:
            return self.parent.config.device_specific_actions_require_auth

    async def send_need_admin_auth_and_check_response(self,password,action):
        await self.response_manager.send_basic_response("needs-admin-auth",action = action)
        if await self.parent.is_authed(self.websocket,password):
            return True
        else:
            return False

"""
The class that handles all special action protocols that aren't "basic".
"basic" actions are ones that involves one request and one response, 
"special" actions require more communication.
"""

class SpecialActionHandler:
    def __init__(self):
        pass
    
    async def execute_special_action(self,action,bot_websocket,client_websocket):
        pass
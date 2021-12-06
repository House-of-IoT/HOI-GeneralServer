from datetime import datetime
"""
TBD: Futher Capture expansion

This class contains all of the dict creations that we need to pass to the capture manager to complete
a successful capture. a basic dict(created by create_basic_dict())
wraps a capture dict with its type capture type opcode and it is sent to the capture manager to be 
parsed and captured.

"""
class CaptureDictCreator:

    @staticmethod
    def create_basic_dict(type_data,data):
        return {
            "type":type_data,
            "data":data
        }
    
    @staticmethod 
    def create_action_dict(client_name,bot_name,action,bot_type):
        return {
            "executor":client_name,
            "bot_name":bot_name,
            "date":datetime.utcnow(),
            "bot_type":bot_type,
            "action":action
        }
    
    @staticmethod
    def create_contact_dict(name,number,add_or_remove):
        return{
            "name":name,
            "number":number,
            "type": add_or_remove
        }
    
    @staticmethod 
    def create_banned_dict(ip,type_data):
        return{
            "ip":ip,
            "type":type_data
        }

    @staticmethod
    def create_connection_dict(name,type_data):
        return {
            "name":name,
            "type":type_data,
            "date":datetime.utcnow()
        }
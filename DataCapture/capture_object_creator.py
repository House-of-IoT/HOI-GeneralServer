from datetime import datetime
"""
TBD: Futher Capture expansion
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
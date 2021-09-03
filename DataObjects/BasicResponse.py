import json

class BasicResponse:
    def __init__(self,server_name):
        self.server_name = server_name
        self.action = None
        self.status = None
        self.bot_name = None
        self.target = None
        self.target_value = None

    def string_version(self):
        data_dict = {
            "server_name" : self.server_name,
            "action" : self.action,
            "status" : self.status,
            "bot_name" : self.bot_name,
            "target" : self.target,
            "target_value" : self.target_value
        }
        return json.dumps(data_dict)
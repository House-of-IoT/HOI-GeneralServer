import json

class BasicResponse:
    def __init__(self,server_name):
        self.server_name = server_name
        self.action = None
        self.status = None
        self.bot_name = None

    def string_version(self):
        data_dict = {
            "server_name" : self.server_name,
            "action" : self.action,
            "response" : self.response,
            "status" : self.status,
            "bot_name" : self.bot_name
        }

        return json.loads(data_dict)
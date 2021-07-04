import json

class ServerStateResponse:
    def __init__(self,server_name):
        self.state_target = None
        self.state_value = None
        self.status = None
        self.server_name = server_name

    def string_version(self):
        data_holder = {}
        data_holder["state_target"] = self.state_target
        data_holder["state_value"] = self.state_value
        data_holder["status"] = self.status
        data_holder["server_name"] = self.server_name
        return json.dumps(data_holder)
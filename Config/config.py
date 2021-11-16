import json

class ConfigHandler:
    def __init__(self):
        self.disconnecting_requires_admin = False
        self.activating_requires_admin = True
        self.deactivating_requires_admin = False
        self.viewing_all_devices_requires_auth = True
        self.device_specific_actions_require_auth = True
        self.using_sql = False
        self.host = None
        self.port = None
        self.grab_current_config()

    def grab_current_config(self):
        with open ("config.json",'r') as File:
            data = File.read()
            try:
                data_dict = json.loads(data)
                self.disconnecting_requires_admin = data_dict["disconnecting"]
                self.activating_requires_admin = data_dict["activating"]
                self.viewing_all_devices_requires_auth = data_dict["viewing"]
                self.deactivating_requires_admin = data_dict["deactivating"]
                self.host = data_dict["host"]
                self.port = data_dict["port"]
                self.using_sql = data_dict["using_sql"]
                self.device_specific_actions_require_auth = data_dict["device_specific"]
            except Exception as e:
                print(e)
                print("There is an issue with the required config.json...")
                input("Press enter to quit....")
                quit()
                
    def string_version(self):
        data_dict = {
            "disconnecting" : self.disconnecting_requires_admin,
            "activating" : self.activating_requires_admin,
            "deactivating" : self.deactivating_requires_admin,
            "viewing" : self.viewing_all_devices_requires_auth
        }
        return json.dumps(data_dict)

class ConfigMaker:
    def welcome(self):
        print("Welcome to HOI-GeneralServer config maker!\n")
        print("Fill out the below information to generate a configuration file for server settings\n")
        print("Note:You could just change the settings from one of the clients, this is just for initialization")

    def make_config(self):
        disconnecting = input("\nDisconnecting bots(smart devices) requires admin authentication[Y,N]:")
        activating = input("\nActivating bots(smart devices) requires admin authentication[Y,N]:")
        deactivating = input("\nDeactivating bots(smart devices) requires admin authentication[Y,N]:")
        viewing = input("\nViewing all devices connected to the server requires admin authentication[Y,N]:")
        host = input("\nHost:")
        port = int(input("Port:"))
        using_sql = input("Using sql[Y,N]:")
        device_specific_actions = input("Device specific actions require authentication[Y,N]:")

        data_dict = {}
        data_dict["disconnecting"] = self.route_bool(disconnecting)
        data_dict["activating"] = self.route_bool(activating)
        data_dict["deactivating"] = self.route_bool(deactivating)
        data_dict["viewing"] = self.route_bool(viewing)
        data_dict["host"] = host
        data_dict["port"] = port
        data_dict["using_sql"] = self.route_bool(using_sql)
        data_dict["device_specific"] = self.route_bool(device_specific_actions)
        self.write_config(data_dict)

    def write_config(self,data_dict):
        with open("config.json" , "w") as File:
            data_to_write =json.dumps(data_dict)
            File.write(data_to_write)

    def route_bool(self,value):
        if (value == "Y" or value == "y"):
            return True
        else:   
            return False

if __name__ == "__main__":
    maker = ConfigMaker()
    maker.welcome()
    maker.make_config()
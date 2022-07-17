import json

class ConfigHandler:
    def __init__(self):
        # The config for things that does
        # and dpes not require admin auth
        self.disconnecting_requires_admin = False
        self.activating_requires_admin = True
        self.deactivating_requires_admin = False
        self.viewing_all_devices_requires_auth = True
        self.device_specific_actions_require_auth = True
        self.relations_editing_requires_admin_auth = True
        self.adding_custom_types_requires_admin_auth = True
        # Other Config
        self.using_sql = False
        self.host = None
        self.port = None
        self.external_controller_location = None
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
                self.external_controller_location = data_dict["external_controller_location"]
                self.relations_editing_requires_admin_auth = data_dict["relations"]
                self.adding_custom_types_requires_admin_auth = data_dict["add_custom_types"]
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
            "viewing" : self.viewing_all_devices_requires_auth,
            "using_sql": self.using_sql,
            "device_specific":self.device_specific_actions_require_auth,
            "relations":self.relations_editing_requires_admin_auth,
            "add_custom_types":self.adding_custom_types_requires_admin_auth
        }
        return json.dumps(data_dict)

class ConfigMaker:
    def welcome(self):
        print("Welcome to HOI-GeneralServer config maker!\n")
        print("Fill out the below information to generate a configuration file for server settings\n")
        print("Note:You could just change the settings from one of the clients, this is just for initialization\n")
        print("Note:Please know that these settings are important to how you structure your user base(who can do what with what password)\n")

    def make_config(self):
        disconnecting = input("\nDisconnecting bots(smart devices) requires admin authentication[Y,N]:")
        activating = input("\nActivating bots(smart devices) requires admin authentication[Y,N]:")
        deactivating = input("\nDeactivating bots(smart devices) requires admin authentication[Y,N]:")
        viewing = input("\nViewing all devices connected to the server requires admin authentication[Y,N]:")
        host = input("\nHost:")
        port = int(input("\nPort:"))
        using_sql = input("\nUsing sql[Y,N]:")
        device_specific_actions = input("\nDevice specific actions require admin authentication[Y,N]:")
        external_controller_location = input("\nExternal Controller location(include ws:// or wss://):")
        relations = input("\nRelation modification of the external controller requires admin authentication:[Y,N]:")
        add_custom_types = input("Adding custom device types requires admin authentication[Y,N]:")

        data_dict = {}
        data_dict["disconnecting"] = self.route_bool(disconnecting)
        data_dict["activating"] = self.route_bool(activating)
        data_dict["deactivating"] = self.route_bool(deactivating)
        data_dict["viewing"] = self.route_bool(viewing)
        data_dict["host"] = host
        data_dict["port"] = port
        data_dict["using_sql"] = self.route_bool(using_sql)
        data_dict["device_specific"] = self.route_bool(device_specific_actions)
        data_dict["external_controller_location"] = external_controller_location
        data_dict["relations"] = self.route_bool(relations)
        data_dict["add_custom_types"] = self.route_bool(add_custom_types)
        self.write_config(json.dumps(data_dict))
        
    def write_config(self,data_to_write):
        with open("config.json" , "w") as File:
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
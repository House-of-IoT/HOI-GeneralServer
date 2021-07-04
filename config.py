import json

class ConfigHandler:
    def __init__(self):
        self.disconnecting_requires_admin = False
        self.activating_requires_admin = False
        self.deactivating_requires_admin = False
        self.viewing_all_devices_requires_auth = False

    def grab_current_config(self):
        with open ("config.json",'r') as File:
            data = File.readlines()
            try:
                data_dict = json.loads(data)
                self.disconnecting_requires_admin = data_dict["disconnecting"]
                self.activating_requires_admin = data_dict["activating"]
                self.viewing_all_devices_requires_auth = data_dict["viewing"]
                self.deactivating_requires_admin = data_dict["deactivating"]
            except:
                pass

class ConfigMaker:
    def welcome(self):
        print("Welcome to HOI-GeneralServer config maker!\n")
        print("Fill out the below information to generate a configuration file for server settings\n")


    def make_config(self):
        disconnecting = input("Disconnecting bots(smart devices) requires admin authentication[Y,N]:")
        activating = input("activating bots(smart devices) requires admin authentication[Y,N]:")
        deactivating = input("deactivating bots(smart devices) requires admin authentication[Y,N]:")
        viewing = input("viewing all devices connected to the server requires admin authentication[Y,N]:")

            
            
import json
from os import name

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
                print("There is an issue with the required config.json...")
                input("Press enter to quit....")
                quit()


class ConfigMaker:
    def welcome(self):
        print("Welcome to HOI-GeneralServer config maker!\n")
        print("Fill out the below information to generate a configuration file for server settings\n")
        print("Note:You could just change the settings from one of the clients, this is just for initialization")

    def make_config(self):
        disconnecting = input("\nDisconnecting bots(smart devices) requires admin authentication[Y,N]:")
        activating = input("\nactivating bots(smart devices) requires admin authentication[Y,N]:")
        deactivating = input("\ndeactivating bots(smart devices) requires admin authentication[Y,N]:")
        viewing = input("\nviewing all devices connected to the server requires admin authentication[Y,N]:")

        data_dict = {}
        data_dict["disconnecting"] = self.route_bool(disconnecting)
        data_dict["activating"] = self.route_bool(activating)
        data_dict["deactivating"] = self.route_bool(deactivating)
        data_dict["viewing"] = self.route_bool(viewing)
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
            
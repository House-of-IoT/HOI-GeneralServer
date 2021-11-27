from termcolor import colored
from colorama import init

class ConsoleLogger:
    def __init__(self,parent):
        self.row_number = 0
        self.parent = parent

    def start_message(self):
        print("\x1B[2J\x1B[1;1H") #console cleared
        print("Server Started....\n")
        print(colored("[~] House of Iot ", "red") + colored("General Server ","green") +colored("Version 1.0.0\n","red"))
        print(colored("Source code: https://github.com/House-of-IoT\n"))
        print(colored("Got an issue?: https://github.com/House-of-IoT/HOI-GeneralServer/issues\n" , "green"))

    def log_name_check_error(self,name):
        self.log_generic_row(f"There was an attempt to connect as '{name}' in the check declaration that failed" , "red")
        self.log_name_error_info()

    def log_name_error_info(self):
        self.log_info("Try waiting 5 seconds before connecting a second time\n")

    def log_info(self, data):
        print(colored("[Info] ~ ","yellow") + data)

    def log_generic_row(self,data,color):
        print(colored(f"[{self.row_number}] ~ ",color) + data)
        self.row_number += 1

    def log_disconnect(self,name):
        print(colored(f"[-] ~ ","red") +f"'{name}' was disconnected from the server\n")
        self.log_device_stats()

    def log_device_stats(self):
        self.log_info(f"There are {len(self.parent.devices.keys())} devices currently connected to the server")
        
    def log_undetected_bot(self,name):
        self.log_generic_row(f"'{name}' has made a request for a bot that is not connected","red")
        self.log_device_stats()

    def log_new_connection(self,name,client_type):
        print(colored(f"[+] New Connection '{name}' with type : {client_type}\n","green"))
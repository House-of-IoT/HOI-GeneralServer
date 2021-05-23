import asyncio
import json

class Main:
    def __init__(self):
        self.clients = {}
        self.clients_type = {}
        self.accepted_types = {"reed_switch" , 
            "gas_smoke_fire_detector" , "ralph" , "home_watcher"}
        self.connected = 0

    async def check_type(self):
        pass


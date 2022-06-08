from DataObjects.type_capabilities import Capabilities
import json

class TypeHandler:
    def __init__(self):
        self.accepted_types = {
            "reed_switch":Capabilities(), 
            "gas_smoke_fire_detector":Capabilities(), 
            "ralph":Capabilities(
                has_audio_streaming=True, 
                has_video_streaming=True,
                has_ground_movement=True) , 
            "home_watcher":Capabilities(
                has_audio_streaming=True,
                has_video_streaming=True,
                has_pir=True),
            "infared":Capabilities(has_pir=True),
            "non-bot":Capabilities(),
            "test_bot":Capabilities(has_test_trigger=True),
            "custom_bot":Capabilities()}
        self.get_custom_types()

    def get_custom_types(self):
        try: 
            with open("custom_accepted_types.json","r") as File:
                data = File.readlines()
                data_dict = json.loads(data)
                self.set_all_custom_types(data_dict)
        except Exception as e:
            print(e)

    def set_all_custom_types(self,types):
        for key in types.keys():
            if key not in self.accepted_types:
                self.add_custom_type(types[key],key)
   
    def add_custom_type(self,type_data,type_key):
        custom_basic_actions = set(type_data["accepted_basic_actions"])
        has_audio_streaming = type_data["audio"]
        has_video_streaming = type_data["video"]
        has_ground_movement = type_data["ground_movement"]
        has_pir = type_data["has_pir"]
        capabilities = Capabilities(
            has_pir = has_pir,has_audio_streaming = has_audio_streaming,
            has_video_streaming = has_video_streaming,
            has_ground_movement = has_ground_movement,
            accepted_basic_actions = custom_basic_actions,
            original=False)
        self.accepted_types[type_key] = capabilities
        self.update_accepted_types_file()

    def remove_custom_type(self,key):
        #only remove non-originals
        if key in self.accepted_types and self.accepted_types[key].original == False:
            del self.accepted_types[key]
    
    def update_accepted_types_file(self):
        data_dict = {}
        for accepted_key in self.accepted_types.keys():
            capabilities= self.accepted_types[accepted_key]
            if capabilities.original == False:
                data_dict[accepted_key] = {
                    "accepted_basic_actions" : list(
                        capabilities.accepted_basic_actions),
                    "audio": capabilities.functionality["audio_streaming"],
                    "video": capabilities.functionality["video_streaming"],
                    "ground_movement":capabilities.functionality["ground_movement"],
                    "has_pir":capabilities.functionality["pir"]}
        data = json.dumps(data_dict)
        self.write_to_file("custom_accepted_types.json",data)

    def write_to_file(self,file_name,data):
        with open(file_name,"w") as File:
            File.write(data)

    def is_valid(self,type_str):
        if type_str in self.accepted_types:
            return True
        else:
            return False
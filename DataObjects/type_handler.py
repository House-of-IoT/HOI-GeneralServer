from DataObjects.type_capabilities import Capabilities

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
            "test_bot":Capabilities(has_test_trigger=True)}

    def set_custom_types(self,types):
        try:
            for key in types.keys():
                custom_basic_actions = set(types[key]["accepted_basic_actions"])
                has_audio_streaming = types[key]["audio"]
                has_video_streaming = types[key]["video"]
                has_ground_movement = types[key]["ground_movement"]
                has_pir = types[key]["has_pir"]
                capabilities = Capabilities(
                    has_pir = has_pir,has_audio_streaming = has_audio_streaming,
                    has_video_streaming = has_video_streaming,
                    has_ground_movement = has_ground_movement,
                    accepted_basic_actions = custom_basic_actions)
                if key not in self.accepted_types:
                    self.accepted_types[key] = capabilities
        except Exception as e:
            print(e)

    def is_valid(self,type_str):
        if type_str in self.accepted_types:
            return True
        else:
            return False
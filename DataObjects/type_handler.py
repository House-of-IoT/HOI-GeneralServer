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
            "non-bot":Capabilities()}

    def is_valid(self,type_str):
        if type_str in self.accepted_types:
            return True
        else:
            return False
    

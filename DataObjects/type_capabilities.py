class Capabilities:
    def __init__(self,has_pir = False,
        has_video_streaming = False,has_audio_streaming = False,
        has_ground_movement=False, has_test_trigger = False,
        accepted_basic_actions = set()):

        #non basic functionality the server can handle
        self.functionality = {
            "video_streaming" : has_video_streaming,
            "audio_streaming" : has_audio_streaming,
            "ground_movement" : has_ground_movement,
            "pir" : has_pir,
            "test_trigger": has_test_trigger}

        #for custom types only 
        self.accepted_basic_actions = accepted_basic_actions
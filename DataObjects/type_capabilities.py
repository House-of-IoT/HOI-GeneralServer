class Capabilities:
    def __init__(self,has_pir = False,
        has_video_streaming = False,has_audio_streaming = False,
        has_ground_movement=False, has_test_trigger = False):
        self.functionality = {
            "video_streaming" : has_video_streaming,
            "audio_streaming" : has_audio_streaming,
            "ground_movement" : has_ground_movement,
            "pir" : has_pir,
            "test_trigger": has_test_trigger
        } 
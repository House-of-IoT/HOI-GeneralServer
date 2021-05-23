class Capabilities:
    def __init__(self,has_pir = False,
        has_video_streaming = False,has_audio_streaming = False,
        has_ground_movement=False):
        self.has_pir = has_pir
        self.has_video_streaming = has_video_streaming
        self.has_audio_streaming = has_audio_streaming
        self.has_ground_movement = has_ground_movement

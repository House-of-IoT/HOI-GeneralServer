class BotHandler:
    def __init__(self,parent,name,websocket, client_type):
        self.parent = parent
        self.name = name
        self.websocket = websocket
        self.type = client_type

    def check_capabilites_and_begin(self):
        capabilities = self.parent.accepted_types[self.types]
        if capabilities.has_audio_streaming:
            pass
        elif capabilities.has_video_streaming:
            pass
        elif capabilities.has_pir:
            pass
        elif capabilities.has_ground_movement:
            pass
    


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
    
    async def check_should_start_streaming(self):
        print("checking")
        sent_status = self.parent.stream_request_already_sent[self.name]
        available_status = self.parent.available_status[self.name]
        if  available_status == False and  sent_status == False:
            await self.websocket.send("stream")
            self.parent.stream_request_already_sent[self.name] = True
            print("sending.. stream_request")
    


class BotHandler:
    def __init__(self,parent,name,websocket, client_type):
        self.parent = parent
        self.name = name
        self.websocket = websocket
        self.type = client_type

    async def check_capabilites_and_begin(self):
        capabilities = self.parent.accepted_types[self.type]
        if capabilities.functionality["audio_streaming"]:
            await self.check_should_start_audio_streaming()
        elif capabilities.functionality["video_streaming"]:
            await self.check_should_start_video_streaming()
        elif capabilities.functionality["pir"]:
            self.check_should_start_motion_alerts()
        elif capabilities.functionality["ground_movement"]:
            self.check_should_start_listening_for_movement()
    
    async def check_should_start_motion_alerts(self):
        pass

    async def check_should_start_listening_for_movement(self):
        pass


    #fix streaming logic
    async def check_should_start_video_streaming(self):
        sent_status = self.parent.video_stream_request_already_sent[self.name]
        available_status = self.parent.available_status[self.name]
        if  available_status == False and  sent_status == False:
            await self.websocket.send("video_stream")
            self.parent.video_stream_request_already_sent[self.name] = True
            print("sending.. video_stream_request")

    async def check_should_start_audio_streaming(self):
        sent_status = self.parent.audio_stream_request_already_sent[self.name]
        available_status = self.parent.available_status[self.name]
        if  available_status == False and  sent_status == False:
            await self.websocket.send("audio_stream")
            self.parent.audio_stream_request_already_sent[self.name] = True
            print("sending.. audio_stream_request")
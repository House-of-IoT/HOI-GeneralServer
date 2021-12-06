from datetime import datetime
import asyncio

class NotificationHandler:
    def __init__(self,parent):
        self.current_notifications = {}
        self.parent = parent
    
    def create_notification(self,message,fatal):
        self.add_new_devices_to_current_notifications()
        notification = {"message":message, "time":datetime.utcnow(), "fatal":fatal}
        for key in self.current_notifications.keys():
            self.current_notifications[key].append(notification)
    
    def serve_notifications(self,name):
        if name in self.current_notifications:
            self.convert_notification_times_to_str(self.current_notifications[name])
            notifications = self.current_notifications[name]
            #reset notifications
            self.current_notifications[name] = []
            return notifications
        else:
            return []
    
    #add all non-bots to the notification subscription
    def add_new_devices_to_current_notifications(self):
        for key in self.parent.devices.keys():
            if self.parent.devices_type[key] == "non-bot":
                if key not in self.current_notifications:
                    self.current_notifications[key] = []

    def convert_notification_times_to_str(self,notifications):
        for notification in notifications:
            notification["time"] = str(notification["time"])

    def cleanup_all_notifications(self):
        dict_keys = list(self.current_notifications.keys())
        for key in dict_keys:
            if key not in self.parent.devices or "ExternalMonitor" in key:
                del self.current_notifications[key]

    async def cleanup_all_notifications_forever(self):
        while True:
            try:
                self.cleanup_all_notifications()
            except Exception as e:
                print(e)
            await asyncio.sleep(12)
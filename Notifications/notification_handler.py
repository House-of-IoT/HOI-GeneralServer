from datetime import datetime
import asyncio

class NotificationHandler:
    def __init__(self,parent):
        self.current_notifications = {}
        self.parent = parent
    
    def create_notification(self,message,fatal):
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
    
    def convert_notification_times_to_str(self,notifications):
        for notification in notifications:
            notification["time"] = str(notification["time"])

    async def cleanup_notifications(self):
        while True:
            try:
                for key in self.current_notifications.keys():
                    if key not in self.parent.devices or "ExternalMonitor" in key:
                        del self.current_notifications[key]
            except Exception as e:
                print(e)
            await asyncio.sleep(12)
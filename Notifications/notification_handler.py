from datetime import datetime

class NotificationHandler:
    def __init__(self):
        self.current_notifications = {}
    
    def add_generic_notification_to_all(self,notification):
        pass
    
    def create_notification(self,message):
        notification = {"message":message, "time":datetime.utcnow()}
        for key in self.current_notifications.keys():
            self.current_notifications[key].append(notification)    
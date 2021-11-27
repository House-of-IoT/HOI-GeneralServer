from twilio.rest import Client
import os

class TwilioHandler:
    def __init__(self,parent):
        self.account_sid =os.environ.get("hoi_t_account_sid")
        self.auth_token = os.environ.get("hoi_t_auth_token")
        self.phone_number = os.environ.get("hoi_t_phone_number")
        self.client = Client(self.account_sid, self.auth_token)
        self.parent = parent

    def send_notification(self,body,to):
        try:
            self.client.messages.create(
                        body=body,
                        from_=self.phone_number,
                        to= to)
            self.parent.console_logger.log_generic_row(f"Sending Notification to {to}!","green")
        except:
            pass
    
    def send_notifications_to_all(self,message):
        contacts = self.parent.contacts.keys()
        for contact in contacts:
            self.send_notification(message,self.parent.contacts[contact])
        self.parent.console_logger.log_generic_row("Sent all contacts a notification!","green")
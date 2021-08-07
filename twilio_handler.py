from twilio.rest import Client

class TwilioHandler:

    def __init__(self,account_sid, auth_token,phone_number,parent):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.phone_number = phone_number
        self.client = Client(self.account_sid, self.auth_token)
        self.parent = parent

    def send_notification(self,body,to):
        self.client.messages.create(
                     body=body,
                     from_=self.phone_number,
                     to= to)
        self.parent.console_logger.log_generic_row(f"Sending Notification to {to}!","green")
    
    def send_notifications_to_all(self,message):
        contacts = self.parent.contacts.keys()
        for contact in contacts:
            self.send_notification(message,self.parent.contacts[contact])
        self.parent.console_logger.log_generic_row("Sent all contacts a notification!","green")

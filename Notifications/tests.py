import re
import unittest
from notification_handler import NotificationHandler

class MockParent:
    def __init__(self):
        #simulating the devices of our Main class in main.py
        self.devices = {
            "test_device":None,
            "test_device1":None}
        self.devices_type = {
            "test_device":"non-bot",
            "test_device1":"non-bot"}

class Tests(unittest.IsolatedAsyncioTestCase):
    async def test(self):
        parent = MockParent()
        notification_handler = NotificationHandler(parent)
        self.adding_new_device_keys_to_notification_handler(notification_handler,parent)
        self.notification_cleanup(notification_handler)
        self.notification_creation(notification_handler,parent)
        self.notification_serving(notification_handler,parent)
    
    def notification_cleanup(self, notification_handler):
        print("testing notification cleanup...")
        #no calls ever access this interal structure but we are to enforce the rule that
        # the external monitor doesn't hold notifications. It should be cleaned up via logic.
        notification_handler.current_notifications["ExternalMonitor"] = [{}]
        self.assertEqual(len(notification_handler.current_notifications["ExternalMonitor"]),1)
        notification_handler.cleanup_all_notifications()
        self.assertTrue("ExternalMonitor" not in notification_handler.current_notifications)
    
        #remove notifications of disconnected device
        #this bot will not exist in parent.devices so it should be cleaned up
        #this key should no longer exist in current_notifications after running cleanup
        notification_handler.current_notifications["test_111"] = [{}]
        self.assertTrue("test_111" in notification_handler.current_notifications)
        notification_handler.cleanup_all_notifications()
        self.assertFalse("test_111" in notification_handler.current_notifications)
    
    def notification_creation(self,notification_handler,mock_parent):
        print("testing notification creation...")
        notification_handler.create_notification("test",False)
        #every non-bot in our parent(mock_parent in this case) should get the notification
        #since we only have non-bots in our mock parent every device should get it.
        for key in mock_parent.devices.keys():
            self.assertEqual(len(notification_handler.current_notifications[key]),1)
            notification_just_added = notification_handler.current_notifications[key][0]
            self.assertEqual(notification_just_added["message"],"test")
            self.assertEqual(notification_just_added["fatal"],False)
        
    def notification_serving(self,notification_handler,mock_parent):
        #make sure the serve method works as expected
        #and the side effects of serving happens
        #this test assumes notification_creation was successful in the previous test.
        print("testing notification serving...")
        for key in mock_parent.devices.keys():
            result = notification_handler.serve_notifications(key)
            self.assertEqual(len(result),1)
            self.assertEqual(result[0]["message"],"test")
            self.assertTrue("time" in  result[0])
            self.assertEqual(result[0]["fatal"], False)
            #make sure the notifications are getting reset after the serve
            result = notification_handler.serve_notifications(key)
            self.assertEqual(len(result),0)
    
    def adding_new_device_keys_to_notification_handler(self,notification_handler,mock_parent):
        #make sure that the notification handler is matching our device's keys
        #to the interal current_notifications dict. This method being tested is called in create_notification()
        print("testing adding new device keys(making sure all devices have an initialized list)")
        mock_parent.devices["test_add"] = None
        mock_parent.devices_type["test_add"] = "non-bot"
        self.assertTrue("test_add" not in notification_handler.current_notifications)
        notification_handler.add_new_devices_to_current_notifications()
        self.assertTrue("test_add" in notification_handler.current_notifications)
        self.assertEqual(len(notification_handler.current_notifications["test_add"]),0)
        del mock_parent.devices["test_add"]
        del mock_parent.devices_type["test_add"]
        del notification_handler.current_notifications["test_add"]

if __name__ == "__main__":
    unittest.main()
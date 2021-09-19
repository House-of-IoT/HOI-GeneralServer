# This module aims at testing the underlying logic of the auto scheduler.

from asyncio import tasks
import datetime
from unittest.case import TestCase
import auto_scheduler

class MockParentForScheduler:
    def __init__(self,available_status,parent_devices):
        self.available_status = available_status
        self.parent_devices = parent_devices

class Tests(TestCase):
    
    def test(self):
        task_one = auto_scheduler.Task(datetime.datetime.utcnow(),"test_bot","test")
        task_two = auto_scheduler.Task(datetime.datetime.utcnow() + datetime.timedelta(days = 3),"test_bot","test")
        available_status = {"test_bot":True}
        parent_devices = {"test_bot":"WEBSOCKET_PLACEHOLDER_BUT_FOR_TEST"}
        mock_parent = MockParentForScheduler(available_status,parent_devices)
        scheduler = auto_scheduler.AutoScheduler()

        self.should_execute(task_one,scheduler,1)
        self.should_execute(task_one,scheduler,2)

    def should_execute(self,task,scheduler,case):
        result = scheduler.task_should_run(task)
        #task's time should be before now, so it should be true
        if case == 1:
            self.assertTrue(result)

        # task's time should be a few days after now, so it should be false
        elif case == 2:
            self.assertFalse(result)
        
    def adding_task(self,task,mock_parent,scheduler):



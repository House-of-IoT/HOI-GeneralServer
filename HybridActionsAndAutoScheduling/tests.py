# This module aims at testing the underlying logic of the auto scheduler.

from asyncio import tasks
import datetime
from unittest.case import TestCase
import unittest
import auto_scheduler

class MockParentForScheduler:
    def __init__(self,available_status,parent_devices):
        self.available_status = available_status
        self.devices = parent_devices

class Tests(TestCase):
    def test(self):
        task_one = auto_scheduler.Task(datetime.datetime.utcnow(),"test_bot","test")
        task_two = auto_scheduler.Task(datetime.datetime.utcnow() + datetime.timedelta(days = 3),"test_bot","test")
        available_status = {"test_bot":True}
        parent_devices = {"test_bot":"WEBSOCKET_PLACEHOLDER_BUT_FOR_TEST"}
        mock_parent = MockParentForScheduler(available_status,parent_devices)
        scheduler = auto_scheduler.AutoScheduler(10,mock_parent)

        self.should_execute(task_one,scheduler,1)
        self.should_execute(task_two,scheduler,2)
        self.adding_task(task_one,scheduler)

    def should_execute(self,task,scheduler,case):
        result = scheduler.task_should_run(task)
        #task's time should be before now, so it should be true
        if case == 1:
            self.assertTrue(result)

        # task's time should be a few days after now, so it should be false
        elif case == 2:
            self.assertFalse(result)
        
    def adding_task(self,task,scheduler):
        #make sure task is not present
        uid = str(task.time) + task.bot_name + task.action
        task_not_in_scheduler = uid not in scheduler.tasks
        self.assertTrue(task_not_in_scheduler)

        #add and make sure task is present
        scheduler.add_task(task)
        task_now_exists_in_scheduler = uid in scheduler.tasks
        self.assertTrue(task_now_exists_in_scheduler)

    def canceling_task(self,task,scheduler):
        #Add and make sure task is present
        scheduler.add_task(task)
        uid = str(task.time) + task.bot_name + task.action
        task_now_in_scheduler = uid in scheduler.tasks
        self.assertTrue(task_now_in_scheduler)

        #cancel and make sure task is not present
        scheduler.cancel_task(task)
        task_not_in_scheduler = uid not in scheduler.tasks
        self.assertTrue(task_not_in_scheduler)


if __name__ == "__main__":
    unittest.main()
# This module aims at testing the underlying logic of the auto scheduler.
import asyncio
import datetime
from unittest.case import TestCase
from unittest import IsolatedAsyncioTestCase
import unittest
import auto_scheduler

class MockParentForScheduler:
    def __init__(self,available_status,parent_devices):
        self.available_status = available_status
        self.devices = parent_devices
        self.most_recent_scheduled_tasks = {}

#used to mock the data flow and test executing logic
class MockWebsocket:
    async def recv(self):
        await asyncio.sleep(1)
        return "success"

    async def send(self,message):
        await asyncio.sleep(1)

class Tests(TestCase):
    def test(self):
        task_one = auto_scheduler.Task(datetime.datetime.utcnow(),"test_bot","test")
        task_two = auto_scheduler.Task(datetime.datetime.utcnow() + datetime.timedelta(days = 3),"test_bot","test")
        mock_websocket = MockWebsocket()

        available_status = {"test_bot":True}
        parent_devices = {"test_bot":mock_websocket}

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


        '''
    this test doesn't actually test the 
    end action execution because
    action exectuion is dynamic and
    testing action execution would be nearly impossible.

    this method tests that action execution
    has the expected state side effects.
    '''
class AsyncTests(IsolatedAsyncioTestCase):

    async def test(self):
        #task should execute due to the utcnow being gathered before the executing's utcnow
        task_one = auto_scheduler.Task(datetime.datetime.utcnow(),"test_bot","test")
        mock_websocket = MockWebsocket()

        available_status = {"test_bot":True}
        parent_devices = {"test_bot":mock_websocket}

        mock_parent = MockParentForScheduler(available_status,parent_devices)
        scheduler = auto_scheduler.AutoScheduler(10,mock_parent)
        await self.execution_worked(task_one,scheduler)

    async def execution_worked(self,task,scheduler):

        #clean slate
        bot_has_no_recent_scheduled_tasks = task.bot_name not in scheduler.parent.most_recent_scheduled_tasks
        self.assertTrue(bot_has_no_recent_scheduled_tasks)

        #add task and try to execute
        scheduler.add_task(task)
        await scheduler.try_to_execute_one_task()

        #after execution verify it is saved in memory
        bot_has_recent_scheduled_task = task.bot_name in scheduler.parent.most_recent_scheduled_tasks
        self.assertTrue(bot_has_recent_scheduled_task)

        #verify removal after execution
        task_uid = str(task.time) + task.bot_name + task.action
        task_no_longer_exist = task_uid not in scheduler.tasks
        self.assertTrue(task_no_longer_exist)


    
    

if __name__ == "__main__":
    unittest.main()
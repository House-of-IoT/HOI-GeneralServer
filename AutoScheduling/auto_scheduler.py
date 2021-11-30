import asyncio
import datetime
from DataCapture.capture_object_creator import CaptureDictCreator
"""
Handles auto schedule execution and tasking.
"""
class AutoScheduler:
    def __init__(self,interval,parent):
         self.tasks = {}
         self.check_interval = interval
         self.parent = parent
         self.running = True

    async def execute_tasks(self):
        while True:
            await asyncio.sleep(self.check_interval)
            try:
                await self.try_to_execute_one_task()
            except Exception as e:
                print(e)

    async def try_to_execute_one_task(self):
        tasks = list(self.tasks.keys())
        for task_uid in tasks:
            task = self.tasks[task_uid]
            #if the scheduled time has passed or it is the scheduled time

            if self.task_should_run(task):
                self.parent.available_status[task.bot_name] = False
                await self.send_action_to_bot(task)
                #cancel since we just executed it
                self.cancel_task(task)
                #release control of the bot
                self.parent.available_status[task.bot_name] = True
                #capture action
                bot_type = self.parent.devices_type[task.bot_name]
                action_capture_data = CaptureDictCreator.create_action_dict("AutoScheduler",task.bot_name,task.action,bot_type)
                basic_capture_dict = CaptureDictCreator.create_basic_dict("executed_action",action_capture_data)

                await self.parent.capture_and_serve_manager.try_to_route_and_capture(basic_capture_dict)

                #only try to execute one task at a time 
                break

    def add_task(self,task):
        uid = str(task.time) + task.bot_name + task.action
        self.tasks[uid] = task

    def cancel_task(self,task):
        uid = str(task.time) + task.bot_name + task.action 
        if uid in self.tasks:
            del self.tasks[uid]
        
    def task_should_run(self,task):
        now = datetime.datetime.utcnow()
        """
        Ignore year month and day, make them the same in both datetime objects,
        we only want to compare the time of day.
        """
        if task.reoccuring:
            task.time.year = now.year
            task.time.day = now.day
            task.time.month = now.month
        #if the task's time has passed or the time is now
        if now >= task.time:
            # if bot is connected and available
            if task.bot_name in self.parent.devices and self.parent.available_status[task.bot_name] == True:
                return True
        return False

    async def send_action_to_bot(self,task):
        try:
            #send the request and gather response
            bot_websocket = self.parent.devices[task.bot_name]
            await asyncio.wait_for(bot_websocket.send(task.action),5)
            response = await asyncio.wait_for(bot_websocket.recv(),8)
            task.complete_task(response)
            self.remove_old_records_if_too_full()
            self.parent.most_recent_executed_tasks.put(task)
            
        except Exception as e:
            task.complete_task("issue_with_response")
            self.remove_old_records_if_too_full()
            self.parent.most_recent_executed_tasks.put(task)

    def tasks_to_dict(self):
        data_holder = {}
        all_task_keys = self.tasks.keys()

        #convert Task objects to dict object
        for key in all_task_keys:
            task = self.tasks[key]
            data_holder[key] = task.task_to_dict()
        return data_holder

    def remove_old_records_if_too_full(self):
        if self.parent.most_recent_executed_tasks.qsize() == 5:
            self.parent.most_recent_executed_tasks.get()

"""
Data representation of an auto scheduled task.
"""
class Task:
    def __init__(self,time,name,action,reoccuring):
        self.time = time
        self.bot_name = name
        self.action = action
        self.time_completed = False
        self.response = None
        self.reoccuring = reoccuring

    def task_to_dict(self):
        data_holder={
            "name":self.bot_name,
            "time":str(self.time),
            "action":self.action,
            "completed":str(self.time_completed),
            "response":self.response,
            "reoccuring":self.reoccuring
        }
        return data_holder

    def complete_task(self,response):
        self.time_completed = datetime.datetime.utcnow()
        self.response = response
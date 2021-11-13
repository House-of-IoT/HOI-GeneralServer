import asyncio
import datetime

"""
Handles auto schedule execution and tasking.
"""
class AutoScheduler:
    def __init__(self,interval,parent):
         self.tasks = {}
         self.check_interval = interval
         self.parent = parent

    def add_task(self,task):
        uid = str(task.time) + task.bot_name + task.action
        self.tasks[uid] = task

    def cancel_task(self,task):
        uid = str(task.time) + task.bot_name + task.action
        del self.tasks[uid]
        
    def task_should_run(self,task):
        #if the task's time has passed or the time is now
        if task.time <= datetime.datetime.utcnow():
            # if bot is connected and available
            if task.bot_name in self.parent.devices and self.parent.available_status[task.bot_name] == True:
                return True
        return False
    
    async def try_to_execute_one_task(self):
        tasks = list(self.tasks.keys())
        for task_uid in tasks:
            task = self.tasks[task_uid]

            #if the scheduled time has passed or it is the scheduled time
            if self.task_should_run(task):
                self.parent.available_status[task.bot_name] = False
                try:
                    #send the request and gather response
                    bot_websocket = self.parent.devices[task.bot_name]
                    await asyncio.wait_for(bot_websocket.send(task.action),5)
                    response = await asyncio.wait_for(bot_websocket.recv(),8)
                    self.parent.most_recent_scheduled_tasks[task.bot_name] = response
                except Exception as e:
                    self.parent.most_recent_scheduled_tasks[task.bot_name] = "failure"
                #remove the task
                self.cancel_task(task)

                #release control of the bot
                self.parent.available_status[task.bot_name] = True

                #only try to execute one task at a time 
                break
                

"""
Data representation of an auto scheduled task.
"""
class Task:
    def __init__(self,time,name,action):
        self.time = time
        self.bot_name = name
        self.action = action

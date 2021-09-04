import datetime
import asyncio

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
    
    async def execute_tasks(self):
        tasks = list(self.tasks.keys())
        for task in tasks:
            #if the scheduled time has passed or it is the scheduled time
            if task.time >= datetime.datetime():
                # if bot is connected and available
                if task.name in self.parent.devices and self.parent.available_status[task.name] == True:
                    self.parent.available_status[task.name] = False
                    try:
                        #send the request and gather response
                        bot_websocket = self.parent.devices[task.name]
                        await asyncio.wait_for(bot_websocket.send(task.action),5)
                        response = await asyncio.wait_for(bot_websocket.recv(),8)
                        self.parent.most_recent_scheduled_tasks[task.name] = response
                    except:
                        self.parent.most_recent_scheduled_tasks[task.name] = "failure"

                    #release control of the bot
                    self.parent.available_status[task.name] = True

                    #only try to execute one task at a time 
                    break
    
    async def handle_super_task(self):
        pass

class Task:
    def __init__(self,time,name,action):
        self.time = time
        self.bot_name = name
        self.action = action
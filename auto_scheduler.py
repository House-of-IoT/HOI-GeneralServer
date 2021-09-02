import datetime

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
    
    def execute_tasks(self):
        tasks = list(self.tasks.keys())
        for task in tasks:
            #if the scheduled time has passed or it is the scheduled time
            if task.time >= datetime.datetime():

class Task:
    def __init__(self,time,name,action):
        self.time = time
        self.bot_name = name
        self.action = action
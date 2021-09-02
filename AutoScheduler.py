class AutoScheduler:
     def __init__(self,interval):
         self.tasks = []
         self.check_interval = interval

class Task:
    def __init__(self,time,name,action):
        self.time = time
        self.name = name
        self.action = action
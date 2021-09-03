
import asyncio
from datetime import datetime
from typing import Text
from action_utils import ActionUtils
from auto_scheduler import Task
import json

class HybridActionHandler:
    def __init__(self,parent):
        self.parent = parent
    
    async def schedule_pre_action(self,websocket,name):
        task_data = await asyncio.wait_for(websocket.recv(),20)
        task_dict = json.loads(task_data)

        utils = ActionUtils(websocket,name)
        result = utils.send_need_admin_auth_and_check_response()
        if(result == True):# auth passed
            utils.send_basic_response("success","scheduled",bot_name=task_dict["bot_name"])
            task = Task(datetime.strptime(task_dict["time"]),task_dict["bot_name"],task_dict["action"])
            self.parent.auto_scheduler.
        else:


        

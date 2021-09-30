import asyncio
from datetime import datetime
from action_utils import ActionUtils
from auto_scheduler import Task
import json

"""
bridges the gap between actions that involve the auto-scheduler and the client handler

provides one central location for actions that need handling across multiple handlers(eg. auto scheduler and client handler)
"""

class HybridActionHandler:
    def __init__(self,parent):
        self.parent = parent

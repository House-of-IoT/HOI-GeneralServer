"""
This class handles the "data catch up"
which is a series of tasks that needs to be
executed after coming out of temp memory mode.

When we disconnect from the database and store
records in memory, we needed a way to get those
records back into the database once we reconnected, 
this singleton is the solution.
"""

class DataCatchUpManager:
    def __init__(self,sql_handler):
        pass
    async def catch_up_contacts(self,contacts):
        pass
    async def catch_up_action_execution(self,execution):
        pass
    async def catch_up_connections(self,connections):
        pass
    async def catch_up_banned(self,banned):
        pass

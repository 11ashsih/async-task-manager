from typing import Dict
from app.models import Task

class InMemoryDB:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}

    async def add_task(self, task: Task):
        self.tasks[task.id] = task
        return task
    
    async def get_all(self):
        return list(self.tasks.values())
    
    async def get(self, task_id: str):
        return self.tasks.get(task_id)
    
    async def delete(self, task_id: str):
        return self.tasks.pop(task_id, None)
    
db = InMemoryDB()
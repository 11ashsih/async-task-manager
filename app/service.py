from app.database import db
from app.models import Task, TaskCreate

async def create_task(data: TaskCreate):
    task = Task(title=data.title)
    return await db.add_task(task)

async def list_task():
    return await db.get_all()

async def mark_complete(task_id: str):
    task = await db.get(task_id)
    if task:
        task.completed = True
    return task

async def delete_task(task_id: str):
    return await db.delete(task_id)



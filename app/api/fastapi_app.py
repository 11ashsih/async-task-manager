"""FastAPI REST API for the Async Task Manager (bonus feature).

Start with:
    uvicorn app.api.fastapi_app:app --reload

Endpoints:
    POST   /tasks           – create a task
    GET    /tasks           – list all tasks (supports ?completed= filter and ?q= search)
    GET    /tasks/{id}      – retrieve a task
    PATCH  /tasks/{id}      – partial update
    DELETE /tasks/{id}      – delete a task
    POST   /tasks/{id}/complete – mark as completed
"""

from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query

from app.models.task import Task, TaskCreate, TaskUpdate
from app.services.task_service import TaskService

app = FastAPI(
    title="Async Task Manager",
    description=(
        "A production-ready async task management API built with "
        "Python, asyncio, Pydantic and FastAPI."
    ),
    version="1.0.0",
)

_service = TaskService()


@app.post("/tasks", response_model=Task, status_code=201, summary="Create a task")
async def create_task(payload: TaskCreate) -> Task:
    """Create a new task.

    Args:
        payload: JSON body conforming to :class:`~app.models.task.TaskCreate`.

    Returns:
        The newly created :class:`~app.models.task.Task`.
    """
    return await _service.create_task(payload)


@app.get("/tasks", response_model=List[Task], summary="List tasks")
async def list_tasks(
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    q: Optional[str] = Query(None, description="Search keyword for task titles"),
) -> List[Task]:
    """List tasks with optional filtering and search.

    Args:
        completed: When provided, return only tasks matching this status.
        q: When provided, return only tasks whose title contains this string.

    Returns:
        A list of matching :class:`~app.models.task.Task` objects.
    """
    if q is not None:
        return await _service.search_tasks(q)
    if completed is not None:
        return await _service.filter_tasks(completed)
    return await _service.list_tasks()


@app.get("/tasks/{task_id}", response_model=Task, summary="Get a task")
async def get_task(task_id: str) -> Task:
    """Retrieve a single task by ID.

    Args:
        task_id: UUID of the task.

    Returns:
        The :class:`~app.models.task.Task`.

    Raises:
        HTTPException: 404 when the task does not exist.
    """
    task = await _service.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    return task


@app.patch("/tasks/{task_id}", response_model=Task, summary="Update a task")
async def update_task(task_id: str, payload: TaskUpdate) -> Task:
    """Partially update a task.

    Args:
        task_id: UUID of the task to update.
        payload: Fields to update.

    Returns:
        The updated :class:`~app.models.task.Task`.

    Raises:
        HTTPException: 404 when the task does not exist.
    """
    task = await _service.update_task(task_id, payload)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    return task


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
async def delete_task(task_id: str) -> None:
    """Delete a task permanently.

    Args:
        task_id: UUID of the task to delete.

    Raises:
        HTTPException: 404 when the task does not exist.
    """
    deleted = await _service.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")


@app.post("/tasks/{task_id}/complete", response_model=Task, summary="Complete a task")
async def complete_task(task_id: str) -> Task:
    """Mark a task as completed.

    Args:
        task_id: UUID of the task.

    Returns:
        The updated :class:`~app.models.task.Task`.

    Raises:
        HTTPException: 404 when the task does not exist.
    """
    task = await _service.complete_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    return task

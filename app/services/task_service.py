"""Business-logic layer for task management.

All public methods are ``async`` so they can be awaited inside an asyncio
event loop.  A logging decorator is applied to every service call for
observability.
"""

import asyncio
import functools
import logging
from typing import Callable, List, Optional, TypeVar

from app.database.in_memory_db import InMemoryDatabase
from app.models.task import Task, TaskCreate, TaskUpdate

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable)


def log_operation(func: F) -> F:
    """Decorator that logs the entry and exit of an async service method.

    Args:
        func: The async function to wrap.

    Returns:
        The wrapped function with logging side-effects.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger.debug("Calling %s with args=%s kwargs=%s", func.__name__, args[1:], kwargs)
        result = await func(*args, **kwargs)
        logger.debug("Finished %s -> %s", func.__name__, result)
        return result

    return wrapper  # type: ignore[return-value]


class TaskService:
    """High-level service for managing tasks.

    Wraps an :class:`~app.database.in_memory_db.InMemoryDatabase` and
    exposes create / read / update / delete operations together with
    filtering and search helpers.
    """

    def __init__(self, db: Optional[InMemoryDatabase] = None) -> None:
        """Initialise the service.

        Args:
            db: An optional database instance.  A fresh
                :class:`~app.database.in_memory_db.InMemoryDatabase` is
                created automatically when no instance is supplied.
        """
        self._db: InMemoryDatabase = db if db is not None else InMemoryDatabase()

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    @log_operation
    async def create_task(self, payload: TaskCreate) -> Task:
        """Create and persist a new task.

        Args:
            payload: Validated :class:`~app.models.task.TaskCreate` data.

        Returns:
            The newly created :class:`~app.models.task.Task`.
        """
        task = Task(title=payload.title)
        return await self._db.save(task)

    @log_operation
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by its identifier.

        Args:
            task_id: UUID string of the task.

        Returns:
            The :class:`~app.models.task.Task`, or ``None`` if not found.
        """
        return await self._db.get(task_id)

    @log_operation
    async def list_tasks(self) -> List[Task]:
        """Return all tasks ordered by creation time (ascending).

        Returns:
            A sorted list of all :class:`~app.models.task.Task` objects.
        """
        tasks = await self._db.get_all()
        return sorted(tasks, key=lambda t: t.created_at)

    @log_operation
    async def update_task(self, task_id: str, payload: TaskUpdate) -> Optional[Task]:
        """Apply a partial update to an existing task.

        Args:
            task_id: UUID string of the task to update.
            payload: Fields to update (``None`` values are ignored).

        Returns:
            The updated :class:`~app.models.task.Task`, or ``None`` if the
            task does not exist.
        """
        task = await self._db.get(task_id)
        if task is None:
            return None

        update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
        updated = task.model_copy(update=update_data)
        return await self._db.save(updated)

    @log_operation
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task permanently.

        Args:
            task_id: UUID string of the task to delete.

        Returns:
            ``True`` when the task was found and deleted, ``False`` otherwise.
        """
        return await self._db.delete(task_id)

    @log_operation
    async def complete_task(self, task_id: str) -> Optional[Task]:
        """Mark a task as completed.

        Args:
            task_id: UUID string of the task to complete.

        Returns:
            The updated :class:`~app.models.task.Task`, or ``None`` if not
            found.
        """
        return await self.update_task(task_id, TaskUpdate(completed=True))

    # ------------------------------------------------------------------
    # Filtering & search
    # ------------------------------------------------------------------

    @log_operation
    async def filter_tasks(self, completed: bool) -> List[Task]:
        """Return tasks filtered by completion status.

        Args:
            completed: When ``True``, return only completed tasks; when
                ``False``, return only pending tasks.

        Returns:
            A filtered list of :class:`~app.models.task.Task` objects.
        """
        tasks = await self.list_tasks()
        return [t for t in tasks if t.completed == completed]

    @log_operation
    async def search_tasks(self, keyword: str) -> List[Task]:
        """Search tasks whose title contains *keyword* (case-insensitive).

        Args:
            keyword: The substring to look for in task titles.

        Returns:
            A list of matching :class:`~app.models.task.Task` objects.
        """
        tasks = await self.list_tasks()
        lower = keyword.lower()
        return [t for t in tasks if lower in t.title.lower()]

    # ------------------------------------------------------------------
    # Concurrent helpers
    # ------------------------------------------------------------------

    async def bulk_create_tasks(self, payloads: List[TaskCreate]) -> List[Task]:
        """Create multiple tasks concurrently using :func:`asyncio.gather`.

        This demonstrates concurrent execution: all task-creation
        coroutines are launched simultaneously and their results are
        collected once every coroutine has completed.

        Args:
            payloads: A list of :class:`~app.models.task.TaskCreate` objects.

        Returns:
            A list of newly created :class:`~app.models.task.Task` objects in
            the same order as *payloads*.
        """
        logger.debug("bulk_create_tasks: creating %d tasks concurrently", len(payloads))
        return list(await asyncio.gather(*(self.create_task(p) for p in payloads)))

    async def load_sample_data(self) -> List[Task]:
        """Populate the database with a handful of sample tasks.

        Useful for demos and manual testing.

        Returns:
            The list of created sample :class:`~app.models.task.Task` objects.
        """
        sample_titles = [
            "Set up Python virtual environment",
            "Write project README",
            "Implement async CRUD operations",
            "Add Pydantic data validation",
            "Build CLI menu interface",
            "Write unit tests with pytest",
            "Add FastAPI REST endpoints",
            "Configure logging decorator",
        ]
        payloads = [TaskCreate(title=t) for t in sample_titles]
        tasks = await self.bulk_create_tasks(payloads)
        # Mark first two tasks as already completed to have mixed data
        for task in tasks[:2]:
            await self.complete_task(task.id)
        # Refresh task list so returned objects reflect completed status
        all_tasks = await self.list_tasks()
        return all_tasks

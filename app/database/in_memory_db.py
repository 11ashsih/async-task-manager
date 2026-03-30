"""Async in-memory database backed by a dictionary."""

import asyncio
from typing import Dict, List, Optional

from app.models.task import Task


class InMemoryDatabase:
    """Thread-safe async in-memory storage for tasks.

    Uses a plain dictionary as the backing store and an asyncio.Lock to
    serialise concurrent writes so the class is safe for use inside a
    single-process asyncio application.
    """

    def __init__(self) -> None:
        """Initialise an empty task store."""
        self._store: Dict[str, Task] = {}
        self._lock: asyncio.Lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------

    async def save(self, task: Task) -> Task:
        """Persist a task (insert or replace).

        Args:
            task: The :class:`Task` instance to save.

        Returns:
            The saved task.
        """
        async with self._lock:
            self._store[task.id] = task
        return task

    async def get(self, task_id: str) -> Optional[Task]:
        """Retrieve a single task by its identifier.

        Args:
            task_id: UUID string of the task.

        Returns:
            The matching :class:`Task`, or ``None`` if not found.
        """
        return self._store.get(task_id)

    async def get_all(self) -> List[Task]:
        """Return every task in insertion order.

        Returns:
            A list of all stored :class:`Task` objects.
        """
        return list(self._store.values())

    async def delete(self, task_id: str) -> bool:
        """Remove a task from the store.

        Args:
            task_id: UUID string of the task to remove.

        Returns:
            ``True`` if the task was found and removed, ``False`` otherwise.
        """
        async with self._lock:
            if task_id in self._store:
                del self._store[task_id]
                return True
        return False

    async def clear(self) -> None:
        """Delete all tasks (used primarily in tests)."""
        async with self._lock:
            self._store.clear()

    def __len__(self) -> int:
        """Return the number of stored tasks."""
        return len(self._store)

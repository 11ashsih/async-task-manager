"""Unit tests for TaskService using pytest and pytest-asyncio."""

import pytest
import pytest_asyncio

from app.database.in_memory_db import InMemoryDatabase
from app.models.task import Task, TaskCreate, TaskUpdate
from app.services.task_service import TaskService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def service() -> TaskService:
    """Return a fresh :class:`TaskService` backed by an empty database."""
    db = InMemoryDatabase()
    return TaskService(db=db)


# ---------------------------------------------------------------------------
# TaskService – create
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_task_returns_task(service: TaskService) -> None:
    """create_task should return a Task with the given title."""
    task = await service.create_task(TaskCreate(title="Buy milk"))
    assert isinstance(task, Task)
    assert task.title == "Buy milk"
    assert task.completed is False
    assert task.id


@pytest.mark.asyncio
async def test_create_task_assigns_unique_ids(service: TaskService) -> None:
    """Two tasks created in sequence must have distinct UUIDs."""
    t1 = await service.create_task(TaskCreate(title="First"))
    t2 = await service.create_task(TaskCreate(title="Second"))
    assert t1.id != t2.id


@pytest.mark.asyncio
async def test_create_task_sets_created_at(service: TaskService) -> None:
    """created_at should be a non-None datetime."""
    task = await service.create_task(TaskCreate(title="Timestamped"))
    assert task.created_at is not None


# ---------------------------------------------------------------------------
# TaskService – list / get
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_tasks_empty(service: TaskService) -> None:
    """list_tasks returns an empty list when no tasks exist."""
    tasks = await service.list_tasks()
    assert tasks == []


@pytest.mark.asyncio
async def test_list_tasks_returns_all(service: TaskService) -> None:
    """list_tasks returns every created task."""
    await service.create_task(TaskCreate(title="A"))
    await service.create_task(TaskCreate(title="B"))
    await service.create_task(TaskCreate(title="C"))
    tasks = await service.list_tasks()
    assert len(tasks) == 3


@pytest.mark.asyncio
async def test_get_task_existing(service: TaskService) -> None:
    """get_task returns the correct task when it exists."""
    created = await service.create_task(TaskCreate(title="Find me"))
    fetched = await service.get_task(created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.title == "Find me"


@pytest.mark.asyncio
async def test_get_task_nonexistent(service: TaskService) -> None:
    """get_task returns None for an unknown ID."""
    result = await service.get_task("non-existent-id")
    assert result is None


# ---------------------------------------------------------------------------
# TaskService – update
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_task_title(service: TaskService) -> None:
    """update_task can change the title of an existing task."""
    task = await service.create_task(TaskCreate(title="Old title"))
    updated = await service.update_task(task.id, TaskUpdate(title="New title"))
    assert updated is not None
    assert updated.title == "New title"
    assert updated.completed is False


@pytest.mark.asyncio
async def test_update_task_nonexistent(service: TaskService) -> None:
    """update_task returns None when the task does not exist."""
    result = await service.update_task("missing", TaskUpdate(title="x"))
    assert result is None


# ---------------------------------------------------------------------------
# TaskService – complete
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_complete_task(service: TaskService) -> None:
    """complete_task marks the task as completed."""
    task = await service.create_task(TaskCreate(title="Do laundry"))
    completed = await service.complete_task(task.id)
    assert completed is not None
    assert completed.completed is True


@pytest.mark.asyncio
async def test_complete_task_nonexistent(service: TaskService) -> None:
    """complete_task returns None when the task does not exist."""
    result = await service.complete_task("ghost-id")
    assert result is None


# ---------------------------------------------------------------------------
# TaskService – delete
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_task(service: TaskService) -> None:
    """delete_task removes the task from the database."""
    task = await service.create_task(TaskCreate(title="Ephemeral"))
    assert await service.delete_task(task.id) is True
    assert await service.get_task(task.id) is None


@pytest.mark.asyncio
async def test_delete_task_nonexistent(service: TaskService) -> None:
    """delete_task returns False when the task does not exist."""
    assert await service.delete_task("nope") is False


# ---------------------------------------------------------------------------
# TaskService – filter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_filter_pending(service: TaskService) -> None:
    """filter_tasks(completed=False) returns only pending tasks."""
    t1 = await service.create_task(TaskCreate(title="Pending"))
    t2 = await service.create_task(TaskCreate(title="Done"))
    await service.complete_task(t2.id)

    pending = await service.filter_tasks(completed=False)
    assert len(pending) == 1
    assert pending[0].id == t1.id


@pytest.mark.asyncio
async def test_filter_completed(service: TaskService) -> None:
    """filter_tasks(completed=True) returns only completed tasks."""
    t1 = await service.create_task(TaskCreate(title="Pending"))
    t2 = await service.create_task(TaskCreate(title="Done"))
    await service.complete_task(t2.id)

    completed = await service.filter_tasks(completed=True)
    assert len(completed) == 1
    assert completed[0].id == t2.id


# ---------------------------------------------------------------------------
# TaskService – search
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_tasks_match(service: TaskService) -> None:
    """search_tasks returns tasks whose titles match the keyword."""
    await service.create_task(TaskCreate(title="Write unit tests"))
    await service.create_task(TaskCreate(title="Deploy to production"))
    await service.create_task(TaskCreate(title="Write documentation"))

    results = await service.search_tasks("write")
    assert len(results) == 2
    titles = {t.title for t in results}
    assert titles == {"Write unit tests", "Write documentation"}


@pytest.mark.asyncio
async def test_search_tasks_case_insensitive(service: TaskService) -> None:
    """search_tasks is case-insensitive."""
    await service.create_task(TaskCreate(title="Buy Groceries"))
    results = await service.search_tasks("GROCERIES")
    assert len(results) == 1


@pytest.mark.asyncio
async def test_search_tasks_no_match(service: TaskService) -> None:
    """search_tasks returns an empty list when no tasks match."""
    await service.create_task(TaskCreate(title="Run linter"))
    results = await service.search_tasks("unicorn")
    assert results == []


# ---------------------------------------------------------------------------
# TaskService – bulk_create / concurrent execution
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_bulk_create_tasks(service: TaskService) -> None:
    """bulk_create_tasks creates all tasks concurrently."""
    payloads = [TaskCreate(title=f"Task {i}") for i in range(5)]
    tasks = await service.bulk_create_tasks(payloads)
    assert len(tasks) == 5
    ids = {t.id for t in tasks}
    assert len(ids) == 5  # all unique


# ---------------------------------------------------------------------------
# InMemoryDatabase – direct tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_db_clear(service: TaskService) -> None:
    """InMemoryDatabase.clear removes all tasks."""
    await service.create_task(TaskCreate(title="Temp"))
    await service._db.clear()
    tasks = await service.list_tasks()
    assert tasks == []

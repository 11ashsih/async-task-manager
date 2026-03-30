"""Interactive CLI for the Async Task Manager.

Run with:
    python main.py
"""

import asyncio
import logging
import sys

from app.models.task import TaskCreate, TaskUpdate
from app.services.task_service import TaskService

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s  %(levelname)-8s  %(name)s – %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SEPARATOR = "─" * 60


def _print_task(task) -> None:  # type: ignore[no-untyped-def]
    """Pretty-print a single task to stdout.

    Args:
        task: A :class:`~app.models.task.Task` instance.
    """
    status = "✅ done" if task.completed else "⏳ pending"
    created = task.created_at.strftime("%Y-%m-%d %H:%M")
    print(f"  [{task.id[:8]}…]  {status}  {created}  {task.title}")


def _print_tasks(tasks) -> None:  # type: ignore[no-untyped-def]
    """Print a numbered list of tasks.

    Args:
        tasks: Iterable of :class:`~app.models.task.Task` instances.
    """
    if not tasks:
        print("  (no tasks found)")
        return
    for i, task in enumerate(tasks, start=1):
        print(f"  {i:>3}. ", end="")
        _print_task(task)


def _menu() -> None:
    """Print the main menu."""
    print(f"\n{SEPARATOR}")
    print("  🗂  Async Task Manager")
    print(SEPARATOR)
    print("  1. Add task")
    print("  2. List all tasks")
    print("  3. List pending tasks")
    print("  4. List completed tasks")
    print("  5. Complete a task")
    print("  6. Update task title")
    print("  7. Delete a task")
    print("  8. Search tasks")
    print("  9. Load sample data")
    print("  0. Exit")
    print(SEPARATOR)


def _prompt(message: str) -> str:
    """Display a prompt and return stripped user input.

    Args:
        message: The prompt string shown to the user.

    Returns:
        The stripped input string.
    """
    return input(f"  {message}: ").strip()


# ---------------------------------------------------------------------------
# CLI handlers
# ---------------------------------------------------------------------------

async def handle_add(service: TaskService) -> None:
    """Prompt for a title and create a new task.

    Args:
        service: The :class:`~app.services.task_service.TaskService` instance.
    """
    title = _prompt("Task title")
    if not title:
        print("  ⚠  Title cannot be empty.")
        return
    task = await service.create_task(TaskCreate(title=title))
    print(f"\n  ✅ Created task [{task.id[:8]}…]")


async def handle_list(service: TaskService) -> None:
    """List all tasks.

    Args:
        service: The :class:`~app.services.task_service.TaskService` instance.
    """
    tasks = await service.list_tasks()
    print(f"\n  All tasks ({len(tasks)}):")
    _print_tasks(tasks)


async def handle_filter(service: TaskService, completed: bool) -> None:
    """List tasks filtered by completion status.

    Args:
        service: The :class:`~app.services.task_service.TaskService` instance.
        completed: ``True`` for completed tasks, ``False`` for pending.
    """
    label = "completed" if completed else "pending"
    tasks = await service.filter_tasks(completed)
    print(f"\n  {label.capitalize()} tasks ({len(tasks)}):")
    _print_tasks(tasks)


async def handle_complete(service: TaskService) -> None:
    """Prompt for a task ID prefix and mark that task completed.

    Args:
        service: The :class:`~app.services.task_service.TaskService` instance.
    """
    tasks = await service.list_tasks()
    _print_tasks(tasks)
    if not tasks:
        return
    raw = _prompt("Task ID (first 8 chars or full UUID)")
    prefix = raw.lower()
    matches = [t for t in tasks if t.id.startswith(prefix)]
    if not matches:
        print("  ⚠  No task found with that ID.")
        return
    if len(matches) > 1:
        print("  ⚠  Ambiguous prefix – please use more characters.")
        return
    updated = await service.complete_task(matches[0].id)
    if updated:
        print(f"\n  ✅ Task [{updated.id[:8]}…] marked as completed.")


async def handle_update(service: TaskService) -> None:
    """Prompt for a task ID and new title, then apply the update.

    Args:
        service: The :class:`~app.services.task_service.TaskService` instance.
    """
    tasks = await service.list_tasks()
    _print_tasks(tasks)
    if not tasks:
        return
    raw = _prompt("Task ID (first 8 chars or full UUID)")
    prefix = raw.lower()
    matches = [t for t in tasks if t.id.startswith(prefix)]
    if not matches:
        print("  ⚠  No task found with that ID.")
        return
    if len(matches) > 1:
        print("  ⚠  Ambiguous prefix – please use more characters.")
        return
    new_title = _prompt("New title")
    if not new_title:
        print("  ⚠  Title cannot be empty.")
        return
    updated = await service.update_task(matches[0].id, TaskUpdate(title=new_title))
    if updated:
        print(f"\n  ✅ Task [{updated.id[:8]}…] updated.")


async def handle_delete(service: TaskService) -> None:
    """Prompt for a task ID and delete it.

    Args:
        service: The :class:`~app.services.task_service.TaskService` instance.
    """
    tasks = await service.list_tasks()
    _print_tasks(tasks)
    if not tasks:
        return
    raw = _prompt("Task ID (first 8 chars or full UUID)")
    prefix = raw.lower()
    matches = [t for t in tasks if t.id.startswith(prefix)]
    if not matches:
        print("  ⚠  No task found with that ID.")
        return
    if len(matches) > 1:
        print("  ⚠  Ambiguous prefix – please use more characters.")
        return
    confirm = _prompt(f"Delete '{matches[0].title}'? [y/N]")
    if confirm.lower() != "y":
        print("  Cancelled.")
        return
    deleted = await service.delete_task(matches[0].id)
    if deleted:
        print("  🗑  Task deleted.")


async def handle_search(service: TaskService) -> None:
    """Prompt for a keyword and search task titles.

    Args:
        service: The :class:`~app.services.task_service.TaskService` instance.
    """
    keyword = _prompt("Search keyword")
    if not keyword:
        print("  ⚠  Keyword cannot be empty.")
        return
    results = await service.search_tasks(keyword)
    print(f"\n  Results for '{keyword}' ({len(results)}):")
    _print_tasks(results)


async def handle_sample(service: TaskService) -> None:
    """Load and display sample tasks.

    Args:
        service: The :class:`~app.services.task_service.TaskService` instance.
    """
    print("  Loading sample data…")
    tasks = await service.load_sample_data()
    print(f"\n  Sample data loaded ({len(tasks)} tasks):")
    _print_tasks(tasks)


# ---------------------------------------------------------------------------
# Main event loop
# ---------------------------------------------------------------------------

async def main() -> None:
    """Entry point: run the interactive CLI menu until the user exits."""
    service = TaskService()
    actions = {
        "1": lambda: handle_add(service),
        "2": lambda: handle_list(service),
        "3": lambda: handle_filter(service, completed=False),
        "4": lambda: handle_filter(service, completed=True),
        "5": lambda: handle_complete(service),
        "6": lambda: handle_update(service),
        "7": lambda: handle_delete(service),
        "8": lambda: handle_search(service),
        "9": lambda: handle_sample(service),
    }

    while True:
        _menu()
        choice = _prompt("Choose an option")

        if choice == "0":
            print("\n  Goodbye! 👋\n")
            break

        handler = actions.get(choice)
        if handler is None:
            print("  ⚠  Invalid option. Please choose 0–9.")
            continue

        try:
            await handler()
        except KeyboardInterrupt:
            print("\n  Interrupted.")
            break
        except Exception as exc:  # pragma: no cover
            logger.exception("Unexpected error: %s", exc)
            print(f"  ❌ Error: {exc}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n  Goodbye! 👋\n")
        sys.exit(0)

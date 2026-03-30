# 🗂 Async Task Manager

A **production-ready** Python project that demonstrates async programming,
clean architecture, data validation with Pydantic, a CLI interface, a FastAPI
REST API, and a full pytest test suite.

---

## ✨ Features

| Category | Details |
|---|---|
| **Architecture** | Modular – `app/models`, `app/services`, `app/database`, `app/api` |
| **Task model** | `id` (UUID), `title`, `completed`, `created_at` |
| **CRUD** | Create · Read · Update · Delete |
| **Async** | All DB / service operations are `async`; `asyncio.gather` for concurrent bulk creation |
| **Validation** | Pydantic v2 models with field constraints |
| **Storage** | In-memory dictionary database (`InMemoryDatabase`) |
| **CLI** | Interactive menu (add, list, complete, delete, search, filter) |
| **Logging** | `@log_operation` decorator on every service method |
| **Filtering** | Separate views for pending and completed tasks |
| **Search** | Case-insensitive keyword search across task titles |
| **FastAPI** | Full REST API (bonus) |
| **Tests** | pytest + pytest-asyncio unit tests |

---

## 📁 Project Structure

```
async-task-manager/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py            # Pydantic Task, TaskCreate, TaskUpdate
│   ├── database/
│   │   ├── __init__.py
│   │   └── in_memory_db.py    # Async in-memory dictionary store
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py    # Business logic + logging decorator
│   └── api/
│       ├── __init__.py
│       └── fastapi_app.py     # FastAPI REST API (bonus)
├── tests/
│   ├── __init__.py
│   └── test_task_service.py   # pytest unit tests
├── main.py                    # Interactive CLI entry point
├── requirements.txt
├── pyproject.toml             # pytest configuration
└── README.md
```

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/11ashsih/async-task-manager.git
cd async-task-manager
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 💻 Usage

### Interactive CLI

```bash
python main.py
```

Menu options:

```
──────────────────────────────────────────────────────────
  🗂  Async Task Manager
──────────────────────────────────────────────────────────
  1. Add task
  2. List all tasks
  3. List pending tasks
  4. List completed tasks
  5. Complete a task
  6. Update task title
  7. Delete a task
  8. Search tasks
  9. Load sample data
  0. Exit
──────────────────────────────────────────────────────────
```

### FastAPI REST API

```bash
uvicorn app.api.fastapi_app:app --reload
```

Open **http://127.0.0.1:8000/docs** for the interactive Swagger UI.

| Method | Path | Description |
|---|---|---|
| `POST` | `/tasks` | Create a task |
| `GET` | `/tasks` | List all tasks (supports `?completed=` and `?q=`) |
| `GET` | `/tasks/{id}` | Get a task |
| `PATCH` | `/tasks/{id}` | Update a task |
| `DELETE` | `/tasks/{id}` | Delete a task |
| `POST` | `/tasks/{id}/complete` | Mark task completed |

#### Example

```bash
# Create
curl -X POST http://localhost:8000/tasks \
     -H "Content-Type: application/json" \
     -d '{"title": "Write README"}'

# List pending
curl "http://localhost:8000/tasks?completed=false"

# Search
curl "http://localhost:8000/tasks?q=readme"
```

---

## 🧪 Tests

```bash
pytest
```

The test suite covers:

- Task creation (unique IDs, timestamps)
- List / get operations
- Partial updates
- Completion flow
- Deletion
- Filtering (pending / completed)
- Keyword search (case-insensitive)
- Concurrent bulk creation with `asyncio.gather`
- Database `clear()` helper

---

## 🏗 Architecture Notes

### Async design

Every database and service method is declared `async` so it can be called
inside any `asyncio` event loop.  The `InMemoryDatabase` protects writes
with `asyncio.Lock` to prevent data-races under concurrent access.

### Concurrent execution

`TaskService.bulk_create_tasks` uses `asyncio.gather` to create multiple
tasks simultaneously — a concrete demonstration of concurrent async
execution.

### Logging decorator

`@log_operation` wraps every public service method.  It logs the method
name, arguments and return value at `DEBUG` level so you can trace exactly
what the service is doing without polluting normal output.

---

## 🔮 Future Improvements

- Persist tasks to SQLite / PostgreSQL via SQLAlchemy (async) or Tortoise-ORM
- Add JWT authentication to the FastAPI layer
- Add pagination and sorting to the list endpoint
- Dockerise the FastAPI application
- Add integration tests with `httpx.AsyncClient`
- CI/CD pipeline with GitHub Actions
- Task priorities and due dates
- Real-time updates via WebSockets

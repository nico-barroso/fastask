 > 🇪🇸 [Versión en español](README_ES.md)

# FastTask — REST API with FastAPI

Task and list management REST API built with FastAPI and Pydantic v2.

---

## Architecture decisions

### Model separation
Distinct Pydantic models with clear responsibilities:
- `CreateTask` / `CreateList` — only accepts fields the client can send
- `UpdateTask` / `UpdateList` — all fields optional for partial updates
- `GetTask` / `GetList` — response model, includes server-generated fields

The server controls `id`, `is_completed` and `is_deleted` at all times — the client can never manipulate them directly.

### Single source of truth
The task-list relationship is managed solely from `task.list_id`. Lists do not store references to their tasks — tasks are the source of truth. Each list's `task_count` is calculated at query time by cross-referencing both storages.

> Deleting a list does not delete its tasks. Tasks remain active and accessible, and their management is the client's responsibility. This is a direct consequence of tasks being the source of truth, not lists.

### Centralized exceptions
All HTTP errors are defined in `exceptions/exceptions.py` as reusable static methods organized by type. This avoids repeating `raise HTTPException(...)` in every endpoint and centralizes error messages.

### UUIDs as identifiers
`uuid4` is used instead of sequential IDs to avoid collisions and avoid exposing the volume of data in the API.

### Flexible pagination
Listing endpoints support two modes: by `page` (page number) or by `skip`/`limit` (manual offset). If `page` is provided, it overrides `skip` automatically. The logic is centralized in `dependencies/pagination.py` using FastAPI's dependency injection system (`Depends`), avoiding repetition across endpoints.

>[!Warning]
> **Known limitation:** pagination is applied after loading the entire JSON into memory. With a high volume of data this would be the first bottleneck. The structural solution is to migrate to a database that supports `LIMIT/OFFSET` at query level.

### Task and list isolation
Delete and update operations on lists **do not propagate** to their tasks. Deleting a list does not delete its tasks — they remain active and accessible. This is a conscious decision: the API treats each resource independently and delegates to the client the decision of what to do with orphaned tasks (reassign, delete, etc.).

### Soft delete
Tasks and lists are never directly removed from storage. Deleting an entity marks it as `is_deleted: true`, hiding it from all active listings. This allows restoring them and maintaining a history. Hard delete exists as an explicit and destructive operation.

>[!IMPORTANT]
> ### Hard delete with safety barrier
> Hard delete (permanent) is only allowed on entities already in soft-deleted state. Attempting to hard delete an active entity returns a `409 Conflict`. This creates intentional friction to avoid accidental data loss.

---

## Structure

```
fastask/
├── data/
│   ├── data_handler.py     # JSON read and write
│   ├── tasks.json          # Task storage
│   └── lists.json          # List storage
├── dependencies/
│   └── pagination.py       # Reusable pagination dependency
├── exceptions/
│   └── exceptions.py       # Centralized HTTP exceptions
├── routers/
│   ├── tasks.py            # Task endpoints
│   └── lists.py            # List endpoints
├── schemas/
│   ├── task_models.py      # Task Pydantic models
│   ├── list_models.py      # List Pydantic models
│   └── responses.py        # Generic ApiResponse[T] wrapper
├── tests/
│   ├── test_tasks.py       # Task endpoint tests
│   ├── test_lists.py       # List endpoint tests
│   └── test_exceptions.py  # Exception tests
├── main.py
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Endpoints

### Tasks `/tasks`

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/tasks` | List active tasks (with search and pagination) |
| `GET` | `/tasks/completed` | List completed tasks |
| `GET` | `/tasks/deleted` | List deleted tasks |
| `GET` | `/tasks/{id}` | Get task by ID |
| `POST` | `/tasks` | Create task |
| `PATCH` | `/tasks/{id}` | Update title or description |
| `PATCH` | `/tasks/{id}/completed` | Mark as completed |
| `PATCH` | `/tasks/{id}/uncompleted` | Mark as not completed |
| `PATCH` | `/tasks/{id}/add/{list_id}` | Add task to a list |
| `PATCH` | `/tasks/{id}/remove/{list_id}` | Remove task from a list |
| `PATCH` | `/tasks/{id}/restore` | Restore deleted task |
| `DELETE` | `/tasks/{id}` | Soft delete |
| `DELETE` | `/tasks/{id}/hard` | Hard delete (permanent) — must be soft-deleted first |

### Lists `/lists`

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/lists` | List active lists (with search and pagination) |
| `GET` | `/lists/deleted` | List deleted lists |
| `GET` | `/lists/{id}` | Get list by ID |
| `GET` | `/lists/{id}/tasks` | Get tasks in a list |
| `POST` | `/lists` | Create list |
| `PATCH` | `/lists/{id}` | Update title or description |
| `PATCH` | `/lists/{id}/restore` | Restore deleted list |
| `DELETE` | `/lists/{id}` | Soft delete |
| `DELETE` | `/lists/{id}/hard` | Hard delete (permanent) — must be soft-deleted first |

---

## Stack

- **Python 3.12**
- **FastAPI**
- **Pydantic v2**
- **Uvicorn**
- **Docker + docker-compose**

---

## Running the project

### From GHCR (recommended)

```bash
docker pull ghcr.io/nico-barroso/fastask:latest
docker run -p 8000:8000 ghcr.io/nico-barroso/fastask:latest
```

### With Docker

```bash
docker compose up
```

### Without Docker

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Interactive documentation will be available at `http://127.0.0.1:8000/docs`.

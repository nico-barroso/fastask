import copy
from unittest.mock import patch

TASKS = [
    {
        "id": "task-1",
        "title": "Task One",
        "description": None,
        "is_completed": False,
        "is_deleted": False,
        "list_id": None,
    },
    {
        "id": "task-2",
        "title": "Task Two",
        "description": "A description",
        "is_completed": True,
        "is_deleted": False,
        "list_id": None,
    },
    {
        "id": "task-3",
        "title": "Task Three",
        "description": None,
        "is_completed": False,
        "is_deleted": True,
        "list_id": None,
    },
    {
        "id": "task-4",
        "title": "Task In List",
        "description": None,
        "is_completed": False,
        "is_deleted": False,
        "list_id": "list-1",
    },
]

LISTS = [
    {"id": "list-1", "title": "List One", "description": None, "is_deleted": False},
    {"id": "list-2", "title": "List Deleted", "description": None, "is_deleted": True},
]


def tasks():
    return copy.deepcopy(TASKS)


def lists():
    return copy.deepcopy(LISTS)


# --- GET /tasks/ ---

def test_get_tasks_returns_only_active(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()):
        response = client.get("/tasks/")
    assert response.status_code == 200
    assert all(not t["is_deleted"] for t in response.json()["data"])


def test_get_tasks_empty(client):
    with patch("routers.tasks.load_tasks", return_value=[]):
        response = client.get("/tasks/")
    assert response.status_code == 200
    assert response.json()["data"] == []
    assert response.json()["message"] == "No tasks found"


def test_get_tasks_search_filters_by_title(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()):
        response = client.get("/tasks/?search=two")
    assert response.status_code == 200
    results = response.json()["data"]
    assert len(results) == 1
    assert results[0]["id"] == "task-2"


def test_get_tasks_pagination(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()):
        response = client.get("/tasks/?page=1&limit=2")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2


# --- GET /tasks/completed ---

def test_get_completed_tasks(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()):
        response = client.get("/tasks/completed")
    assert response.status_code == 200
    assert all(t["is_completed"] for t in response.json()["data"])


def test_get_completed_tasks_empty(client):
    with patch("routers.tasks.load_tasks", return_value=[]):
        response = client.get("/tasks/completed")
    assert response.status_code == 200
    assert response.json()["data"] == []


# --- GET /tasks/deleted ---

def test_get_deleted_tasks(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()):
        response = client.get("/tasks/deleted")
    assert response.status_code == 200
    assert all(t["is_deleted"] for t in response.json()["data"])


# --- GET /tasks/{task_id} ---

def test_get_task_by_id(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()):
        response = client.get("/tasks/task-1")
    assert response.status_code == 200
    assert response.json()["data"]["id"] == "task-1"


def test_get_task_by_id_not_found(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()):
        response = client.get("/tasks/nonexistent")
    assert response.status_code == 404


def test_get_task_by_id_deleted_returns_404(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()):
        response = client.get("/tasks/task-3")
    assert response.status_code == 404


# --- POST /tasks/ ---

def test_create_task(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()), \
         patch("routers.tasks.write_tasks"):
        response = client.post("/tasks/", json={"title": "New Task"})
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["title"] == "New Task"
    assert data["is_completed"] is False
    assert data["is_deleted"] is False
    assert data["list_id"] is None


def test_create_task_with_description(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()), \
         patch("routers.tasks.write_tasks"):
        response = client.post("/tasks/", json={"title": "New Task", "description": "Some desc"})
    assert response.status_code == 201
    assert response.json()["data"]["description"] == "Some desc"


def test_create_task_duplicate_title_returns_409(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()):
        response = client.post("/tasks/", json={"title": "Task One"})
    assert response.status_code == 409


def test_create_task_empty_title_returns_422(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()):
        response = client.post("/tasks/", json={"title": ""})
    assert response.status_code == 422


# --- PATCH /tasks/{task_id} ---

def test_update_task(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()), \
         patch("routers.tasks.write_tasks"):
        response = client.patch("/tasks/task-1", json={"title": "Updated Title"})
    assert response.status_code == 200
    assert response.json()["data"]["title"] == "Updated Title"


def test_update_task_not_found(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()):
        response = client.patch("/tasks/nonexistent", json={"title": "Updated"})
    assert response.status_code == 404


def test_update_deleted_task_returns_404(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()):
        response = client.patch("/tasks/task-3", json={"title": "Updated"})
    assert response.status_code == 404


# --- PATCH /tasks/{task_id}/completed ---

def test_complete_task(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()), \
         patch("routers.tasks.write_tasks"):
        response = client.patch("/tasks/task-1/completed")
    assert response.status_code == 200
    assert response.json()["data"]["is_completed"] is True


def test_complete_task_already_completed_returns_409(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()):
        response = client.patch("/tasks/task-2/completed")
    assert response.status_code == 409


def test_complete_task_not_found(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()):
        response = client.patch("/tasks/nonexistent/completed")
    assert response.status_code == 404


# --- PATCH /tasks/{task_id}/uncompleted ---

def test_uncomplete_task(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()), \
         patch("routers.tasks.write_tasks"):
        response = client.patch("/tasks/task-2/uncompleted")
    assert response.status_code == 200
    assert response.json()["data"]["is_completed"] is False


def test_uncomplete_task_already_uncompleted_returns_409(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()):
        response = client.patch("/tasks/task-1/uncompleted")
    assert response.status_code == 409


# --- PATCH /tasks/{task_id}/add/{list_id} ---

def test_add_task_to_list(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()), \
         patch("routers.tasks.load_lists", return_value=lists()), \
         patch("routers.tasks.write_tasks"):
        response = client.patch("/tasks/task-1/add/list-1")
    assert response.status_code == 200
    assert response.json()["data"]["list_id"] == "list-1"


def test_add_task_to_nonexistent_list_returns_404(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()), \
         patch("routers.tasks.load_lists", return_value=lists()):
        response = client.patch("/tasks/task-1/add/nonexistent")
    assert response.status_code == 404


def test_add_task_to_deleted_list_returns_404(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()), \
         patch("routers.tasks.load_lists", return_value=lists()):
        response = client.patch("/tasks/task-1/add/list-2")
    assert response.status_code == 404


def test_add_nonexistent_task_to_list_returns_404(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()), \
         patch("routers.tasks.load_lists", return_value=lists()):
        response = client.patch("/tasks/nonexistent/add/list-1")
    assert response.status_code == 404


# --- PATCH /tasks/{task_id}/remove/{list_id} ---

def test_remove_task_from_list(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()), \
         patch("routers.tasks.load_lists", return_value=lists()), \
         patch("routers.tasks.write_tasks"):
        response = client.patch("/tasks/task-4/remove/list-1")
    assert response.status_code == 200
    assert response.json()["data"]["list_id"] is None


def test_remove_task_from_wrong_list_returns_400(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()), \
         patch("routers.tasks.load_lists", return_value=lists()):
        response = client.patch("/tasks/task-1/remove/list-1")
    assert response.status_code == 400


def test_remove_nonexistent_task_from_list_returns_404(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()), \
         patch("routers.tasks.load_lists", return_value=lists()):
        response = client.patch("/tasks/nonexistent/remove/list-1")
    assert response.status_code == 404


# --- PATCH /tasks/{task_id}/restore ---

def test_restore_task(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()), \
         patch("routers.tasks.write_tasks"):
        response = client.patch("/tasks/task-3/restore")
    assert response.status_code == 200
    assert response.json()["data"]["is_deleted"] is False


def test_restore_active_task_returns_409(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()):
        response = client.patch("/tasks/task-1/restore")
    assert response.status_code == 409


def test_restore_nonexistent_task_returns_404(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()):
        response = client.patch("/tasks/nonexistent/restore")
    assert response.status_code == 404


# --- DELETE /tasks/{task_id} ---

def test_soft_delete_task(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()), \
         patch("routers.tasks.write_tasks"):
        response = client.delete("/tasks/task-1")
    assert response.status_code == 200
    assert response.json()["data"]["is_deleted"] is True


def test_soft_delete_already_deleted_returns_409(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()):
        response = client.delete("/tasks/task-3")
    assert response.status_code == 409


def test_soft_delete_not_found_returns_404(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()):
        response = client.delete("/tasks/nonexistent")
    assert response.status_code == 404


# --- DELETE /tasks/{task_id}/hard ---

def test_hard_delete_task(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()), \
         patch("routers.tasks.write_tasks"):
        response = client.delete("/tasks/task-1/hard")
    assert response.status_code == 200
    assert response.json()["data"]["id"] == "task-1"


def test_hard_delete_not_found_returns_404(client):
    with patch("routers.tasks.load_tasks", return_value=tasks()):
        response = client.delete("/tasks/nonexistent/hard")
    assert response.status_code == 404

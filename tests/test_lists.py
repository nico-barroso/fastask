import copy
from unittest.mock import patch

LISTS = [
    {"id": "list-1", "title": "List One", "description": None, "is_deleted": False},
    {"id": "list-2", "title": "List Two", "description": "A description", "is_deleted": False},
    {"id": "list-3", "title": "List Deleted", "description": None, "is_deleted": True},
]

TASKS = [
    {
        "id": "task-1",
        "title": "Task One",
        "description": None,
        "is_completed": False,
        "is_deleted": False,
        "list_id": "list-1",
    },
    {
        "id": "task-2",
        "title": "Task Two",
        "description": None,
        "is_completed": False,
        "is_deleted": False,
        "list_id": "list-1",
    },
    {
        "id": "task-3",
        "title": "Task Deleted",
        "description": None,
        "is_completed": False,
        "is_deleted": True,
        "list_id": "list-1",
    },
]


def lists():
    return copy.deepcopy(LISTS)


def tasks():
    return copy.deepcopy(TASKS)


# --- GET /lists/ ---

def test_get_lists_returns_only_active(client):
    with patch("routers.lists.load_lists", return_value=lists()), \
         patch("routers.lists.load_tasks", return_value=tasks()):
        response = client.get("/lists/")
    assert response.status_code == 200
    assert all(not lst["is_deleted"] for lst in response.json()["data"])


def test_get_lists_includes_task_count(client):
    with patch("routers.lists.load_lists", return_value=lists()), \
         patch("routers.lists.load_tasks", return_value=tasks()):
        response = client.get("/lists/")
    list_one = next(l for l in response.json()["data"] if l["id"] == "list-1")
    assert list_one["task_count"] == 2  # task-3 está deleted, no cuenta


def test_get_lists_empty(client):
    with patch("routers.lists.load_lists", return_value=[]), \
         patch("routers.lists.load_tasks", return_value=[]):
        response = client.get("/lists/")
    assert response.status_code == 200
    assert response.json()["data"] == []


def test_get_lists_search(client):
    with patch("routers.lists.load_lists", return_value=lists()), \
         patch("routers.lists.load_tasks", return_value=tasks()):
        response = client.get("/lists/?search=two")
    assert response.status_code == 200
    results = response.json()["data"]
    assert len(results) == 1
    assert results[0]["id"] == "list-2"


def test_get_lists_pagination(client):
    with patch("routers.lists.load_lists", return_value=lists()), \
         patch("routers.lists.load_tasks", return_value=tasks()):
        response = client.get("/lists/?page=1&limit=1")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1


# --- GET /lists/deleted ---

def test_get_deleted_lists(client):
    with patch("routers.lists.load_lists", return_value=lists()):
        response = client.get("/lists/deleted")
    assert response.status_code == 200
    assert all(lst["is_deleted"] for lst in response.json()["data"])


def test_get_deleted_lists_empty(client):
    with patch("routers.lists.load_lists", return_value=[]):
        response = client.get("/lists/deleted")
    assert response.status_code == 200
    assert response.json()["data"] == []


# --- GET /lists/{list_id} ---

def test_get_list_by_id(client):
    with patch("routers.lists.load_lists", return_value=lists()), \
         patch("routers.lists.load_tasks", return_value=tasks()):
        response = client.get("/lists/list-1")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == "list-1"
    assert data["task_count"] == 2


def test_get_list_by_id_not_found(client):
    with patch("routers.lists.load_lists", return_value=lists()), \
         patch("routers.lists.load_tasks", return_value=tasks()):
        response = client.get("/lists/nonexistent")
    assert response.status_code == 404


def test_get_deleted_list_by_id_returns_404(client):
    with patch("routers.lists.load_lists", return_value=lists()), \
         patch("routers.lists.load_tasks", return_value=tasks()):
        response = client.get("/lists/list-3")
    assert response.status_code == 404


# --- GET /lists/{list_id}/tasks ---

def test_get_tasks_by_list(client):
    with patch("routers.lists.load_lists", return_value=lists()), \
         patch("routers.lists.load_tasks", return_value=tasks()):
        response = client.get("/lists/list-1/tasks")
    assert response.status_code == 200
    results = response.json()["data"]
    assert len(results) == 2  # task-3 está deleted, no aparece
    assert all(t["list_id"] == "list-1" for t in results)


def test_get_tasks_by_nonexistent_list_returns_404(client):
    with patch("routers.lists.load_lists", return_value=lists()), \
         patch("routers.lists.load_tasks", return_value=tasks()):
        response = client.get("/lists/nonexistent/tasks")
    assert response.status_code == 404


def test_get_tasks_by_deleted_list_returns_404(client):
    with patch("routers.lists.load_lists", return_value=lists()), \
         patch("routers.lists.load_tasks", return_value=tasks()):
        response = client.get("/lists/list-3/tasks")
    assert response.status_code == 404


# --- POST /lists/ ---

def test_create_list(client):
    with patch("routers.lists.load_lists", return_value=lists()), \
         patch("routers.lists.write_lists"):
        response = client.post("/lists/", json={"title": "New List"})
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["title"] == "New List"
    assert data["is_deleted"] is False


def test_create_list_with_description(client):
    with patch("routers.lists.load_lists", return_value=lists()), \
         patch("routers.lists.write_lists"):
        response = client.post("/lists/", json={"title": "New List", "description": "desc"})
    assert response.status_code == 201
    assert response.json()["data"]["description"] == "desc"


def test_create_list_duplicate_title_returns_409(client):
    with patch("routers.lists.load_lists", return_value=lists()):
        response = client.post("/lists/", json={"title": "List One"})
    assert response.status_code == 409


def test_create_list_empty_title_returns_422(client):
    response = client.post("/lists/", json={"title": ""})
    assert response.status_code == 422


# --- PATCH /lists/{list_id} ---

def test_update_list(client):
    with patch("routers.lists.load_lists", return_value=lists()), \
         patch("routers.lists.load_tasks", return_value=tasks()), \
         patch("routers.lists.write_lists"):
        response = client.patch("/lists/list-1", json={"title": "Updated"})
    assert response.status_code == 200
    assert response.json()["data"]["title"] == "Updated"


def test_update_list_not_found(client):
    with patch("routers.lists.load_lists", return_value=lists()), \
         patch("routers.lists.load_tasks", return_value=tasks()):
        response = client.patch("/lists/nonexistent", json={"title": "Updated"})
    assert response.status_code == 404


def test_update_deleted_list_returns_404(client):
    with patch("routers.lists.load_lists", return_value=lists()), \
         patch("routers.lists.load_tasks", return_value=tasks()):
        response = client.patch("/lists/list-3", json={"title": "Updated"})
    assert response.status_code == 404


# --- PATCH /lists/{list_id}/restore ---

def test_restore_list(client):
    with patch("routers.lists.load_lists", return_value=lists()), \
         patch("routers.lists.load_tasks", return_value=tasks()), \
         patch("routers.lists.write_lists"):
        response = client.patch("/lists/list-3/restore")
    assert response.status_code == 200
    assert response.json()["data"]["is_deleted"] is False


def test_restore_active_list_returns_409(client):
    with patch("routers.lists.load_lists", return_value=lists()), \
         patch("routers.lists.load_tasks", return_value=tasks()):
        response = client.patch("/lists/list-1/restore")
    assert response.status_code == 409


def test_restore_nonexistent_list_returns_404(client):
    with patch("routers.lists.load_lists", return_value=lists()), \
         patch("routers.lists.load_tasks", return_value=tasks()):
        response = client.patch("/lists/nonexistent/restore")
    assert response.status_code == 404


# --- DELETE /lists/{list_id} ---

def test_soft_delete_list(client):
    with patch("routers.lists.load_lists", return_value=lists()), \
         patch("routers.lists.load_tasks", return_value=tasks()), \
         patch("routers.lists.write_lists"):
        response = client.delete("/lists/list-1")
    assert response.status_code == 200
    assert response.json()["data"]["is_deleted"] is True


def test_soft_delete_already_deleted_list_returns_409(client):
    with patch("routers.lists.load_lists", return_value=lists()), \
         patch("routers.lists.load_tasks", return_value=tasks()):
        response = client.delete("/lists/list-3")
    assert response.status_code == 409


def test_soft_delete_list_not_found_returns_404(client):
    with patch("routers.lists.load_lists", return_value=lists()), \
         patch("routers.lists.load_tasks", return_value=tasks()):
        response = client.delete("/lists/nonexistent")
    assert response.status_code == 404


# --- DELETE /lists/{list_id}/hard ---

def test_hard_delete_list(client):
    with patch("routers.lists.load_lists", return_value=lists()), \
         patch("routers.lists.write_lists"):
        response = client.delete("/lists/list-3/hard")
    assert response.status_code == 200
    assert response.json()["data"]["id"] == "list-3"


def test_hard_delete_list_not_found_returns_404(client):
    with patch("routers.lists.load_lists", return_value=lists()):
        response = client.delete("/lists/nonexistent/hard")
    assert response.status_code == 404


def test_hard_delete_active_list_returns_409(client):
    with patch("routers.lists.load_lists", return_value=lists()):
        response = client.delete("/lists/list-1/hard")
    assert response.status_code == 409

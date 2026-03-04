import uuid

from fastapi import APIRouter, Query

from data.data_handler import load_lists, write_lists, load_tasks
from schemas.list_models import GetList, CreateList, UpdateList
from schemas.task_models import GetTask
from schemas.responses import ApiResponse
from exceptions.exceptions import ApiException


def _count_tasks(list_id: str, tasks: list) -> int:
    return sum(1 for t in tasks if t["list_id"] == list_id and not t["is_deleted"])

router = APIRouter(
    prefix="/lists",
    tags=["lists"],
    responses={
        400: {"description": "Bad request"},
        404: {"description": "List not found"},
        409: {"description": "Conflict"},
        500: {"description": "Internal server error"},
    },
)


@router.get("/", response_model=ApiResponse[list[GetList]], summary="Get all lists")
async def get_lists(
    search: str | None = Query(default=None),
    page: int | None = Query(default=None, ge=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
):
    """
    Retrieve a paginated list of active (non-deleted) lists.

    - **search**: Filter lists by title (case-insensitive)
    - **page**: Page number, overrides skip if provided
    - **skip**: Number of lists to skip
    - **limit**: Maximum number of lists to return (1-100)
    """
    lists = [lst for lst in load_lists() if not lst["is_deleted"]]
    tasks = load_tasks()

    if search:
        lists = [lst for lst in lists if search.lower() in lst["title"].lower()]

    if page is not None:
        skip = (page - 1) * limit

    data_counted = []
    for lst in lists[skip : skip + limit]:
        count = sum(1 for tsk in tasks if tsk["list_id"] == lst["id"] and not tsk["is_deleted"])
        lst["task_count"] = count
        data_counted.append(lst)

    return ApiResponse(
        success=True,
        message="Lists retrieved" if lists else "No lists found",
        data=data_counted,
    )


@router.post(
    "/", response_model=ApiResponse[GetList], status_code=201, summary="Create a list"
)
async def create_list(lst: CreateList):
    """
    Create a new list.

    - **title**: Required. Must be unique among active lists
    - **description**: Optional. Description of the list
    """
    lists = load_lists()

    if any(item["title"] == lst.title for item in lists if not item["is_deleted"]):
        ApiException.AlreadyExists.list(lst.title)

    new_list = {
        "id": str(uuid.uuid4()),
        "title": lst.title,
        "description": lst.description,
        "is_deleted": False,
    }

    lists.append(new_list)
    write_lists(lists)

    return ApiResponse(success=True, message="List created", data=new_list)


@router.get(
    "/deleted", response_model=ApiResponse[list[GetList]], summary="Get deleted lists"
)
async def get_deleted_lists(
    page: int | None = Query(default=None, ge=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
):
    """
    Retrieve a paginated list of soft-deleted lists.

    - **page**: Page number, overrides skip if provided
    - **skip**: Number of lists to skip
    - **limit**: Maximum number of lists to return (1-100)
    """
    lists = [lst for lst in load_lists() if lst["is_deleted"]]

    if page is not None:
        skip = (page - 1) * limit

    return ApiResponse(
        success=True,
        message="Deleted lists retrieved" if lists else "No deleted lists found",
        data=lists[skip : skip + limit],
    )


@router.get("/{list_id}", response_model=ApiResponse[GetList], summary="Get list by ID")
async def get_list_by_id(list_id: str):
    """
    Retrieve a single active list by its UUID.

    - **list_id**: UUID of the list to retrieve
    """
    lists = [lst for lst in load_lists() if not lst["is_deleted"]]

    tasks = load_tasks()

    for lst in lists:
        if lst["id"] == list_id:
            lst["task_count"] = _count_tasks(list_id, tasks)
            return ApiResponse(
                success=True, message=f'List "{list_id}" retrieved', data=lst
            )

    ApiException.NotFound.list(list_id)


@router.get(
    "/{list_id}/tasks",
    response_model=ApiResponse[list[GetTask]],
    summary="Get tasks by list",
)
async def get_tasks_by_list(
    list_id: str,
    page: int | None = Query(default=None, ge=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
):
    """
    Retrieve all active tasks belonging to a specific list.

    - **list_id**: UUID of the list
    - **page**: Page number, overrides skip if provided
    - **skip**: Number of tasks to skip
    - **limit**: Maximum number of tasks to return (1-100)
    """
    lists = load_lists()

    for lst in lists:
        if lst["id"] == list_id:
            if lst["is_deleted"]:
                ApiException.NotFound.list(list_id)
            break
    else:
        ApiException.NotFound.list(list_id)

    tasks = [tsk for tsk in load_tasks() if tsk["list_id"] == list_id and not tsk["is_deleted"]]

    if page is not None:
        skip = (page - 1) * limit

    return ApiResponse(
        success=True,
        message=f'Tasks from list "{list_id}" retrieved' if tasks else "No tasks found in this list",
        data=tasks[skip : skip + limit],
    )


@router.patch(
    "/{list_id}", response_model=ApiResponse[GetList], summary="Update a list"
)
async def update_list(list_id: str, lst: UpdateList):
    """
    Update the title and/or description of an existing list.

    - **list_id**: UUID of the list to update
    - **title**: Optional. New title
    - **description**: Optional. New description
    """
    lists = load_lists()

    tasks = load_tasks()

    for item in lists:
        if item["id"] == list_id:
            if item["is_deleted"]:
                ApiException.NotFound.list(list_id)
            item.update(lst.model_dump(exclude_unset=True))
            write_lists(lists)
            item["task_count"] = _count_tasks(list_id, tasks)
            return ApiResponse(success=True, message="List updated", data=item)

    ApiException.NotFound.list(list_id)


@router.patch(
    "/{list_id}/restore",
    response_model=ApiResponse[GetList],
    summary="Restore a deleted list",
)
async def restore_list(list_id: str):
    """
    Restore a soft-deleted list back to active.

    - **list_id**: UUID of the list to restore
    """
    lists = load_lists()

    tasks = load_tasks()

    for lst in lists:
        if lst["id"] == list_id:
            if not lst["is_deleted"]:
                ApiException.AlreadyRestored.list(list_id)
            lst["is_deleted"] = False
            write_lists(lists)
            lst["task_count"] = _count_tasks(list_id, tasks)
            return ApiResponse(
                success=True, message=f'List "{lst["title"]}" restored', data=lst
            )

    ApiException.NotFound.list(list_id)


@router.delete(
    "/{list_id}", response_model=ApiResponse[GetList], summary="Soft delete a list"
)
async def delete_list(list_id: str):
    """
    Soft delete a list. The list remains in storage but is hidden from active listings.

    - **list_id**: UUID of the list to delete
    """
    lists = load_lists()

    tasks = load_tasks()

    for lst in lists:
        if lst["id"] == list_id:
            if lst["is_deleted"]:
                ApiException.AlreadyDeleted.list(list_id)
            lst["is_deleted"] = True
            write_lists(lists)
            lst["task_count"] = _count_tasks(list_id, tasks)
            return ApiResponse(
                success=True, message=f'List "{lst["title"]}" has been deleted', data=lst
            )

    ApiException.NotFound.list(list_id)


@router.delete(
    "/{list_id}/hard", response_model=ApiResponse[GetList], summary="Hard delete a list"
)
async def hard_delete_list(list_id: str):
    """
    Permanently delete a list from storage. This action cannot be undone.

    - **list_id**: UUID of the list to permanently delete
    """
    lists = load_lists()

    deleted_list = next((lst for lst in lists if lst["id"] == list_id), None)

    if deleted_list is None:
        ApiException.NotFound.list(list_id)

    filtered = [lst for lst in lists if lst["id"] != list_id]
    write_lists(filtered)

    return ApiResponse(
        success=True,
        message=f'List "{deleted_list["title"]}" permanently deleted',
        data=deleted_list,
    )
import uuid

from fastapi import APIRouter, Query

from data.data_handler import load_tasks, write_tasks
from exceptions.tasks_exceptions import (
    task_not_found,
    task_already_exists,
    task_already_deleted,
    task_already_completed,
    task_already_uncompleted,
)
from schemas.models import GetTask, UpdateTask, CreateTask
from schemas.responses import ApiResponse

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={
        400: {"description": "Bad request"},
        404: {"description": "Task not found"},
        409: {"description": "Conflict"},
        500: {"description": "Internal server error"},
    },
)


@router.get("/", response_model=ApiResponse[list[GetTask]], summary="Get all tasks")
async def get_tasks(
    page: int | None = Query(default=None, ge=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
):
    """
    Retrieve a paginated list of active (non-deleted) tasks.

    - **page**: Page number, overrides skip if provided
    - **skip**: Number of tasks to skip
    - **limit**: Maximum number of tasks to return (1-100)
    """
    tasks = [t for t in load_tasks() if not t["is_deleted"]]

    if page is not None:
        skip = (page - 1) * limit

    return ApiResponse(
        success=True,
        message="Tasks retrieved" if tasks else "No tasks found",
        data=tasks[skip : skip + limit],
    )


@router.get(
    "/completed",
    response_model=ApiResponse[list[GetTask]],
    summary="Get completed tasks",
)
async def get_completed_tasks(
    page: int | None = Query(default=None, ge=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
):
    """
    Retrieve a paginated list of completed and active (non-deleted) tasks.

    - **page**: Page number, overrides skip if provided
    - **skip**: Number of tasks to skip
    - **limit**: Maximum number of tasks to return (1-100)
    """
    tasks = [t for t in load_tasks() if not t["is_deleted"] and t["is_completed"]]

    if page is not None:
        skip = (page - 1) * limit

    return ApiResponse(
        success=True,
        message="Completed tasks retrieved" if tasks else "No completed tasks found",
        data=tasks[skip : skip + limit],
    )


@router.get(
    "/deleted", response_model=ApiResponse[list[GetTask]], summary="Get deleted tasks"
)
async def get_deleted_tasks(
    page: int | None = Query(default=None, ge=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
):
    """
    Retrieve a paginated list of soft-deleted tasks.

    - **page**: Page number, overrides skip if provided
    - **skip**: Number of tasks to skip
    - **limit**: Maximum number of tasks to return (1-100)
    """
    tasks = [t for t in load_tasks() if t["is_deleted"]]

    if page is not None:
        skip = (page - 1) * limit

    return ApiResponse(
        success=True,
        message="Deleted tasks retrieved" if tasks else "No deleted tasks found",
        data=tasks[skip : skip + limit],
    )


@router.post(
    "/", response_model=ApiResponse[GetTask], status_code=201, summary="Create a task"
)
async def create_task(task: CreateTask):
    """
    Create a new task.

    - **title**: Required. Must be between 1 and 100 characters
    - **description**: Optional. Max 500 characters
    """
    tasks = load_tasks()

    if any(t["title"] == task.title for t in tasks if not t["is_deleted"]):
        task_already_exists(task.title)

    new_task = {
        "id": str(uuid.uuid4()),
        "title": task.title,
        "description": task.description,
        "is_completed": False,
        "is_deleted": False,
    }

    tasks.append(new_task)
    write_tasks(tasks)

    return ApiResponse(success=True, message="Task created", data=new_task)


@router.get("/{task_id}", response_model=ApiResponse[GetTask], summary="Get task by ID")
async def get_task_by_id(task_id: str):
    """
    Retrieve a single active task by its UUID.

    - **task_id**: UUID of the task to retrieve
    """
    tasks = [t for t in load_tasks() if not t["is_deleted"]]

    for t in tasks:
        if t["id"] == task_id:
            return ApiResponse(
                success=True, message=f'Task "{task_id}" retrieved', data=t
            )

    task_not_found(task_id)


@router.patch(
    "/{task_id}", response_model=ApiResponse[GetTask], summary="Update a task"
)
async def update_task(task_id: str, task: UpdateTask):
    """
    Update the title and/or description of an existing task.

    - **task_id**: UUID of the task to update
    - **title**: Optional. New title (1-100 characters)
    - **description**: Optional. New description (max 500 characters)
    """
    tasks = load_tasks()

    for t in tasks:
        if t["id"] == task_id:
            if t["is_deleted"]:
                task_already_deleted(task_id)
            t.update(task.model_dump(exclude_unset=True))
            write_tasks(tasks)
            return ApiResponse(success=True, message="Task updated", data=t)

    task_not_found(task_id)


@router.patch(
    "/{task_id}/completed",
    response_model=ApiResponse[GetTask],
    summary="Complete a task",
)
async def complete_task(task_id: str):
    """
    Mark an active task as completed.

    - **task_id**: UUID of the task to complete
    """
    tasks = load_tasks()

    for t in tasks:
        if t["id"] == task_id:
            if t["is_deleted"]:
                task_not_found(task_id)
            if t["is_completed"]:
                task_already_completed(task_id)

            t["is_completed"] = True
            write_tasks(tasks)
            return ApiResponse(
                success=True, message=f'Task "{t["title"]}" completed', data=t
            )

    task_not_found(task_id)


@router.patch(
    "/{task_id}/uncompleted",
    response_model=ApiResponse[GetTask],
    summary="Uncomplete a task",
)
async def uncomplete_task(task_id: str):
    """
    Mark a completed task as not completed.

    - **task_id**: UUID of the task to uncomplete
    """
    tasks = load_tasks()

    for t in tasks:
        if t["id"] == task_id:
            if t["is_deleted"]:
                task_not_found(task_id)
            if not t["is_completed"]:
                task_already_uncompleted(task_id)

            t["is_completed"] = False
            write_tasks(tasks)
            return ApiResponse(
                success=True, message=f'Task "{t["title"]}" uncompleted', data=t
            )

    task_not_found(task_id)


@router.patch(
    "/{task_id}/restore",
    response_model=ApiResponse[GetTask],
    summary="Restore a deleted task",
)
async def restore_task(task_id: str):
    """
    Restore a soft-deleted task back to active.

    - **task_id**: UUID of the task to restore
    """
    tasks = load_tasks()

    for t in tasks:
        if t["id"] == task_id:
            if not t["is_deleted"]:
                task_not_found(task_id)
            t["is_deleted"] = False
            write_tasks(tasks)
            return ApiResponse(
                success=True, message=f'Task "{t["title"]}" restored', data=t
            )

    task_not_found(task_id)


@router.delete(
    "/{task_id}", response_model=ApiResponse[GetTask], summary="Soft delete a task"
)
async def delete_task(task_id: str):
    """
    Soft delete a task. The task remains in storage but is hidden from active listings.

    - **task_id**: UUID of the task to delete
    """
    tasks = load_tasks()

    for t in tasks:
        if t["id"] == task_id:
            if t["is_deleted"]:
                task_already_deleted(task_id)
            t["is_deleted"] = True
            write_tasks(tasks)
            return ApiResponse(
                success=True, message=f'Task "{t["title"]}" has been deleted', data=t
            )

    task_not_found(task_id)


@router.delete(
    "/{task_id}/hard", response_model=ApiResponse[GetTask], summary="Hard delete a task"
)
async def hard_delete_task(task_id: str):
    """
    Permanently delete a task from storage. This action cannot be undone.

    - **task_id**: UUID of the task to permanently delete
    """
    tasks = load_tasks()

    deleted_task = next((t for t in tasks if t["id"] == task_id), None)

    if deleted_task is None:
        task_not_found(task_id)

    filtered = [t for t in tasks if t["id"] != task_id]
    write_tasks(filtered)

    return ApiResponse(
        success=True,
        message=f'Task "{deleted_task["title"]}" permanently deleted',
        data=deleted_task,
    )

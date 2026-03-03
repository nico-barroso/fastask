from fastapi import APIRouter, Query
from data.data_handler import load_tasks, write_tasks
from schemas.responses import ApiResponse
from schemas.models import *
from exceptions.tasks_exceptions import *

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)


@router.get("/", response_model=ApiResponse[list[GetTask]])
async def get_tasks(
    page: int | None = Query(default=None, ge=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100)
):
    tasks = [t for t in load_tasks() if not t["is_deleted"]]

    if page is not None:
        skip = (page - 1) * limit

    return ApiResponse(
        success=True,
        message="Tasks retrieved" if tasks else "No tasks found",
        data=tasks[skip:skip + limit]
    )


@router.get("/deleted", response_model=ApiResponse[list[GetTask]])
async def get_deleted_tasks(
    page: int | None = Query(default=None, ge=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100)
):
    tasks = [t for t in load_tasks() if t["is_deleted"]]

    if page is not None:
        skip = (page - 1) * limit

    return ApiResponse(
        success=True,
        message="Deleted tasks retrieved" if tasks else "No deleted tasks found",
        data=tasks[skip:skip + limit]
    )


@router.get("/{task_id}", response_model=ApiResponse[GetTask])
async def get_task_by_id(task_id: int):
    tasks = [t for t in load_tasks() if not t["is_deleted"]]

    for t in tasks:
        if t["id"] == task_id:
            return ApiResponse(success=True, message=f'Task "{task_id}" retrieved', data=t)

    task_not_found(task_id)


@router.post("/", response_model=ApiResponse[GetTask], status_code=201)
async def create_task(task: CreateTask):
    tasks = load_tasks()

    if any(t["title"] == task.title for t in tasks if not t["is_deleted"]):
        task_already_exists(task.title)

    new_task = task.model_dump()
    new_task["id"] = len(tasks) + 1
    new_task["is_deleted"] = False

    tasks.append(new_task)
    write_tasks(tasks)

    return ApiResponse(success=True, message="Task created", data=new_task)


@router.patch("/{task_id}", response_model=ApiResponse[GetTask])
async def update_task(task_id: int, task: UpdateTask):
    tasks = load_tasks()

    for t in tasks:
        if t["id"] == task_id:
            if t["is_deleted"]:
                task_already_deleted(task_id)
            t.update(task.model_dump(exclude_unset=True))
            write_tasks(tasks)
            return ApiResponse(success=True, message="Task updated", data=t)

    task_not_found(task_id)


@router.patch("/{task_id}/restore", response_model=ApiResponse[GetTask])
async def restore_task(task_id: int):
    tasks = load_tasks()

    for t in tasks:
        if t["id"] == task_id:
            if not t["is_deleted"]:
                task_already_restored(task_id)
            t["is_deleted"] = False
            write_tasks(tasks)
            return ApiResponse(success=True, message=f'Task "{t["title"]}" restored', data=t)

    task_not_found(task_id)


@router.delete("/{task_id}", response_model=ApiResponse[GetTask])
async def delete_task(task_id: int):
    tasks = load_tasks()

    for t in tasks:
        if t["id"] == task_id:
            if t["is_deleted"]:
                task_already_deleted(task_id)
            t["is_deleted"] = True
            write_tasks(tasks)
            return ApiResponse(success=True, message=f'Task "{t["title"]}" has been deleted', data=t)

    task_not_found(task_id)


@router.delete("/{task_id}/hard", response_model=ApiResponse[GetTask])
async def hard_delete_task(task_id: int):
    tasks = load_tasks()

    deleted_task = next((t for t in tasks if t["id"] == task_id), None)

    if deleted_task is None:
        task_not_found(task_id)

    filtered = [t for t in tasks if t["id"] != task_id]
    write_tasks(filtered)

    return ApiResponse(success=True, message=f'Task "{deleted_task["title"]}" permanently deleted', data=deleted_task)
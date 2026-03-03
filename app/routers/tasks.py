from fastapi import APIRouter, Query, HTTPException
from data.data_handler import load_tasks, write_tasks
from schemas.responses import ApiResponse
from schemas.models import *
from exceptions.tasks_exceptions import *

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)

# Aunque esto es un ejercicio académico, es una buena práctica para que la API
# sea consumida con limitaciones por cuestiones de recursos.
# Tenemos las dos opciones, con paginación tradicional y una con skip para dev
@router.get(
    "/",
    response_model=ApiResponse[list[GetTask]],
    summary="Get all tasks",
    responses={
        200: {"description": "Tasks retrieved successfully"},
    }
)
async def get_tasks(
    page: int | None = Query(default=None, ge=1, description="Page number (overrides skip if provided)"),
    skip: int = Query(default=0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Max number of tasks to return")
):
    """
    Returns a paginated list of active tasks. Supports both skip/limit and page/limit pagination.

    - Use page for page-based pagination
    - Use skip for offset-based pagination
    - limit controls the number of results (max 100)
    """
    tasks = [t for t in load_tasks() if not t["is_deleted"]]

    if page is not None:
        skip = (page - 1) * limit

    return ApiResponse(
        success=True,
        message="Tasks retrieved" if tasks else "No tasks found",
        data=tasks[skip:skip + limit]
    )




@router.get("/{task_id}", response_model=ApiResponse[GetTask], status_code=200)
async def get_task_by_id(
        task_id : int):
    """
    TODO- DOC
    """
    tasks = load_tasks()

    return ApiResponse(
        success=True,
        message=f"Task {task_id} retireved correctly.",
        data=tasks["id" == task_id]
    )


@router.post("/", response_model=ApiResponse[GetTask], status_code=201)
async def create_task(
    task: CreateTask):
    """
    TODO- DOC
    """
    tasks = load_tasks()

    new_task = task.model_dump()
    new_task["id"] = len(tasks) + 1
    new_task["is_deleted"] = False

    tasks.append(new_task)
    write_tasks(tasks)

    return ApiResponse(
        success=True,
        message="Task created",
        data=new_task
    )


@router.patch("/{task_id}", response_model=ApiResponse[GetTask])
async def update_task(
    task_id: int, 
    task: UpdateTask):
    """
    TODO- DOC
    """
    tasks = load_tasks()

    for t in tasks:
        if t["id"] == task_id:
            t.update(task.model_dump(exclude_unset=True))
            write_tasks(tasks)
            return ApiResponse(success=True, message="Task updated", data=t)

  


@router.delete("/{task_id}", response_model=ApiResponse[GetTask])
async def delete_task(
    task_id: int):
    """
    TODO- DOC
    """
    tasks = load_tasks()

    for t in tasks:
        if str(t["id"]) == str(task_id):
            t["is_deleted"] = True
            write_tasks(tasks)
            return ApiResponse(success=True, message=f'Task "{t["title"]}" has been deleted', data=t)




@router.delete("/{task_id}/hard", response_model=ApiResponse[GetTask])
async def hard_delete_task(
    task_id: int):
    """
    TODO- DOC
    """
    tasks = load_tasks()

    filtered = [t for t in tasks if str(t["id"]) != str(task_id)]
    deleted_task = next(t for t in tasks if str(t["id"]) == str(task_id))
    write_tasks(filtered)
    return ApiResponse(success=True, message="Task permanently deleted", data=deleted_task)


@router.patch("/{task_id}/restore", response_model=ApiResponse[GetTask])
async def restore_task(
    task_id: int
    ):
    """
    TODO- DOC
    """
    tasks = load_tasks()

    for t in tasks:
        if str(t["id"]) == str(task_id):
            t["is_deleted"] = False
            write_tasks(tasks)
            return ApiResponse(success=True, message="Task restored", data=t)



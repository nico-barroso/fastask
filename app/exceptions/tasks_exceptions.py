from fastapi import HTTPException


# 400 - Bad Request
def bad_request(detail: str = "Bad request"):
    """Raise a 400 Bad Request exception with a custom or default message."""
    raise HTTPException(status_code=400, detail=detail)


# 404 - Not Found
def task_not_found(task_id: str):
    """Raise a 404 Not Found exception when a task does not exist or is soft-deleted."""
    raise HTTPException(status_code=404, detail=f'Task "{task_id}" not found')


# 409 - Conflict
def task_already_deleted(task_id: str):
    """Raise a 409 Conflict exception when trying to delete an already deleted task."""
    raise HTTPException(status_code=409, detail=f'Task "{task_id}" is already deleted')


def task_already_restored(task_id: str):
    """Raise a 409 Conflict exception when trying to restore an active task."""
    raise HTTPException(status_code=409, detail=f'Task "{task_id}" is already active')


def task_already_completed(task_id: str):
    """Raise a 409 Conflict exception when trying to complete an already completed task."""
    raise HTTPException(
        status_code=409, detail=f'Task "{task_id}" is already completed'
    )


def task_already_uncompleted(task_id: str):
    """Raise a 409 Conflict exception when trying to uncomplete an already uncompleted task."""
    raise HTTPException(
        status_code=409, detail=f'Task "{task_id}" is already uncompleted'
    )


def task_already_exists(title: str):
    """Raise a 409 Conflict exception when a task with the same title already exists."""
    raise HTTPException(
        status_code=409, detail=f'A task with title "{title}" already exists'
    )


# 500 - Internal Server Error
def internal_error(detail: str = "An unexpected error occurred"):
    """Raise a 500 Internal Server Error exception with a custom or default message."""
    raise HTTPException(status_code=500, detail=detail)


def storage_error():
    """Raise a 500 Internal Server Error exception when reading or writing task storage fails."""
    raise HTTPException(status_code=500, detail="Failed to read or write task storage")

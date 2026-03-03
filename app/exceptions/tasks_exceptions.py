from fastapi import HTTPException


# 400 - Bad Request
def bad_request(detail: str = "Bad request"):
    raise HTTPException(status_code=400, detail=detail)


# 404 - Not Found
def task_not_found():
    raise HTTPException(status_code=404, detail=f'Tasks not found')


# 409 - Conflict
def task_already_deleted(task_id: int):
    raise HTTPException(status_code=409, detail=f'Task "{task_id}" is already deleted')

def task_already_restored(task_id: int):
    raise HTTPException(status_code=409, detail=f'Task "{task_id}" is already active')

def task_already_completed(task_id: int):
    raise HTTPException(status_code=409, detail=f'Task "{task_id}" is already completed')

def task_already_exists(title: str):
    raise HTTPException(status_code=409, detail=f'A task with title "{title}" already exists')


# 500 - Internal Server Error
def internal_error(detail: str = "An unexpected error occurred"):
    raise HTTPException(status_code=500, detail=detail)

def storage_error():
    raise HTTPException(status_code=500, detail="Failed to read or write task storage")
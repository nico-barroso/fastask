from fastapi import HTTPException


class ApiException:
    # 404 - Not Found
    def _not_found(entity: str, id: str):
        raise HTTPException(404, detail=f'{entity} "{id}" not found')

    # 409 - Conflict
    def _already_exists(entity: str, title: str):
        raise HTTPException(409, detail=f'{entity} "{title}" already exists.')

    def _already_deleted(entity: str, id: str):
        raise HTTPException(409, detail=f'{entity} "{id}" is already deleted.')

    def _already_restored(entity: str, id: str):
        raise HTTPException(409, detail=f'{entity} "{id}" is already active or has been already restored.')

    def _already_completed(entity: str, id: str):
        raise HTTPException(409, detail=f'{entity} "{id}" is already completed.')

    def _already_uncompleted(entity: str, id: str):
        raise HTTPException(409, detail=f'{entity} "{id}" is already uncompleted.')

    # 500 - Internal Server Error
    def _internal_error(msg: str = "An unexpected error occurred"):
        raise HTTPException(500, detail=f'An unexpected error occurred: {msg}')

    def _storage_error(msg: str = "Failed to read or write storage"):
        raise HTTPException(500, detail=f'Failed to read or write storage: {msg}')


    # 404 Class - Not Found
    class NotFound:
        def list(list_id: str):
            ApiException._not_found("List", list_id)

        def task(task_id: str):
            ApiException._not_found("Task", task_id)


    # 409 Class - Conflict
    class AlreadyExists:
        def list(title: str):
            ApiException._already_exists("List", title)

        def task(title: str):
            ApiException._already_exists("Task", title)

    class AlreadyDeleted:
        def list(list_id: str):
            ApiException._already_deleted("List", list_id)

        def task(task_id: str):
            ApiException._already_deleted("Task", task_id)

    class AlreadyRestored:
        def list(list_id: str):
            ApiException._already_restored("List", list_id)

        def task(task_id: str):
            ApiException._already_restored("Task", task_id)

    class AlreadyCompleted:
        def list(list_id: str):
            ApiException._already_completed("List", list_id)

        def task(task_id: str):
            ApiException._already_completed("Task", task_id)

    class AlreadyUncompleted:
        def list(list_id: str):
            ApiException._already_uncompleted("List", list_id)

        def task(task_id: str):
            ApiException._already_uncompleted("Task", task_id)


    # 500 Class - Internal Server Error
    class InternalError:
        def raise_(msg: str = "An unexpected error occurred"):
            ApiException._internal_error(msg)

    class StorageError:
        def raise_(msg: str = "Failed to read or write storage"):
            ApiException._storage_error(msg)
from fastapi import HTTPException


class ApiException:

    # 400 - Bad Request
    @staticmethod
    def _bad_request(detail: str):
        raise HTTPException(400, detail=detail)

    # 404 - Not Found
    @staticmethod
    def _not_found(entity: str, id: str):
        raise HTTPException(404, detail=f'{entity} "{id}" not found')

    # 409 - Conflict
    @staticmethod
    def _already_exists(entity: str, title: str):
        raise HTTPException(409, detail=f'{entity} "{title}" already exists.')

    @staticmethod
    def _already_deleted(entity: str, id: str):
        raise HTTPException(409, detail=f'{entity} "{id}" is already deleted.')

    @staticmethod
    def _already_restored(entity: str, id: str):
        raise HTTPException(
            409,
            detail=f'{entity} "{id}" is already active or has been already restored.',
        )

    @staticmethod
    def _already_completed(entity: str, id: str):
        raise HTTPException(409, detail=f'{entity} "{id}" is already completed.')

    @staticmethod
    def _already_uncompleted(entity: str, id: str):
        raise HTTPException(409, detail=f'{entity} "{id}" is already uncompleted.')

    # 500 - Internal Server Error
    @staticmethod
    def _internal_error(msg: str = "An unexpected error occurred"):
        raise HTTPException(500, detail=f"An unexpected error occurred: {msg}")

    @staticmethod
    def _storage_error(msg: str = "Failed to read or write storage"):
        raise HTTPException(500, detail=f"Failed to read or write storage: {msg}")
    
    
    # 400 Class - Bad Request
    class BadRequest:
        @staticmethod
        def raise_(task_id: str, list_id: str):
            ApiException._bad_request(
                f'Task "{task_id}" does not belong to list "{list_id}"')

    # 404 Class - Not Found
    class NotFound:
        @staticmethod
        def list(list_id: str):
            ApiException._not_found("List", list_id)

        @staticmethod
        def task(task_id: str):
            ApiException._not_found("Task", task_id)

    # 409 Class - Conflict
    class AlreadyExists:
        @staticmethod
        def list(title: str):
            ApiException._already_exists("List", title)

        @staticmethod
        def task(title: str):
            ApiException._already_exists("Task", title)

    class AlreadyDeleted:
        @staticmethod
        def list(list_id: str):
            ApiException._already_deleted("List", list_id)

        @staticmethod
        def task(task_id: str):
            ApiException._already_deleted("Task", task_id)

    class AlreadyRestored:
        @staticmethod
        def list(list_id: str):
            ApiException._already_restored("List", list_id)

        @staticmethod
        def task(task_id: str):
            ApiException._already_restored("Task", task_id)

    class AlreadyCompleted:
        @staticmethod
        def list(list_id: str):
            ApiException._already_completed("List", list_id)

        @staticmethod
        def task(task_id: str):
            ApiException._already_completed("Task", task_id)

    class AlreadyUncompleted:
        @staticmethod
        def list(list_id: str):
            ApiException._already_uncompleted("List", list_id)

        @staticmethod
        def task(task_id: str):
            ApiException._already_uncompleted("Task", task_id)

    # 500 Class - Internal Server Error
    class InternalError:
        @staticmethod
        def raise_(msg: str = "An unexpected error occurred"):
            ApiException._internal_error(msg)

    class StorageError:
        @staticmethod
        def raise_(msg: str = "Failed to read or write storage"):
            ApiException._storage_error(msg)

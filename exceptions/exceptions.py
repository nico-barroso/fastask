from fastapi import HTTPException


class ApiException:

    # 400 Class - Bad Request
    class BadRequest:
        @staticmethod
        def raise_(task_id: str, list_id: str) -> HTTPException:
            return HTTPException(
                400,
                detail=f'Task "{task_id}" does not belong to list "{list_id}"',
            )

    # 404 Class - Not Found
    class NotFound:
        @staticmethod
        def list(list_id: str) -> HTTPException:
            return HTTPException(404, detail=f'List "{list_id}" not found')

        @staticmethod
        def task(task_id: str) -> HTTPException:
            return HTTPException(404, detail=f'Task "{task_id}" not found')

    # 409 Class - Conflict
    class AlreadyExists:
        @staticmethod
        def list(title: str) -> HTTPException:
            return HTTPException(409, detail=f'List "{title}" already exists.')

        @staticmethod
        def task(title: str) -> HTTPException:
            return HTTPException(409, detail=f'Task "{title}" already exists.')

    class AlreadyDeleted:
        @staticmethod
        def list(list_id: str) -> HTTPException:
            return HTTPException(409, detail=f'List "{list_id}" is already deleted.')

        @staticmethod
        def task(task_id: str) -> HTTPException:
            return HTTPException(409, detail=f'Task "{task_id}" is already deleted.')

    class AlreadyRestored:
        @staticmethod
        def list(list_id: str) -> HTTPException:
            return HTTPException(
                409,
                detail=f'List "{list_id}" is already active or has been already restored.',
            )

        @staticmethod
        def task(task_id: str) -> HTTPException:
            return HTTPException(
                409,
                detail=f'Task "{task_id}" is already active or has been already restored.',
            )

    class AlreadyCompleted:
        @staticmethod
        def task(task_id: str) -> HTTPException:
            return HTTPException(409, detail=f'Task "{task_id}" is already completed.')

    class AlreadyUncompleted:
        @staticmethod
        def task(task_id: str) -> HTTPException:
            return HTTPException(409, detail=f'Task "{task_id}" is already uncompleted.')

    # 500 Class - Internal Server Error
    class InternalError:
        @staticmethod
        def raise_(msg: str = "An unexpected error occurred") -> HTTPException:
            return HTTPException(500, detail=f"An unexpected error occurred: {msg}")

    class StorageError:
        @staticmethod
        def raise_(msg: str = "Failed to read or write storage") -> HTTPException:
            return HTTPException(500, detail=f"Failed to read or write storage: {msg}")

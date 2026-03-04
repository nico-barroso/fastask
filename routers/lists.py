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



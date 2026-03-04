from pydantic import BaseModel, Field
from typing import Optional


class TaskBase(BaseModel):
    """Base task model. The rest of the models inherit from this one."""

    title: str = Field(min_length=1, max_length=100, description="Title of the task")
    description: Optional[str] = Field(
        default=None, max_length=500, description="Optional details about the task"
    )


class GetTask(BaseModel):
    """Response model. Returned by all endpoints."""

    id: str = Field(description="Unique identifier (UUID) of the task")
    title: str = Field(min_length=1, max_length=100, description="Title of the task")
    description: Optional[str] = Field(
        default=None, max_length=500, description="Optional details about the task"
    )
    is_completed: bool = Field(description="Whether the task has been completed")
    is_deleted: bool = Field(description="Whether the task has been soft-deleted")
    list_id: Optional[str] = Field(default=None, description="UUID of the list this task belongs to")


class CreateTask(TaskBase):
    """Input model for creating a new task. Only title and description are accepted — the rest is set by the server."""

    pass


class UpdateTask(BaseModel):
    """Input model for updating an existing task. All fields are optional."""

    title: Optional[str] = Field(
        default=None, max_length=100, description="New title for the task"
    )
    description: Optional[str] = Field(
        default=None, max_length=500, description="New description for the task"
    )
    is_completed: Optional[bool] = Field(
        default=None, description="New completion status for the task"
    )

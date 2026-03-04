from pydantic import BaseModel, Field
from typing import Optional


class ListBase(BaseModel):
    """Base schema with shared fields for list models."""

    title: str = Field(min_length=1, max_length=100, description="List title")
    description: Optional[str] = Field(
        default=None, max_length=500, description="Optional list description"
    )


class GetList(BaseModel):
    """Schema for returning a list in API responses."""

    id: str = Field(description="Unique identifier (UUID)")
    title: str = Field(min_length=1, max_length=100, description="List title")
    description: Optional[str] = Field(
        default=None, max_length=500, description="Optional list description"
    )
    is_deleted: bool = Field(description="Whether the list is soft-deleted")
    task_count: int = Field(default=0, description="Number of active tasks in the list")


class CreateList(ListBase):
    """Schema for creating a new list."""
    pass


class UpdateList(BaseModel):
    """Schema for partially updating an existing list."""

    title: Optional[str] = Field(
        default=None, max_length=100, description="New list title"
    )
    description: Optional[str] = Field(
        default=None, max_length=500, description="New list description"
    )
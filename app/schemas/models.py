from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

# Base task model. The rest of the models inherit from this one.
# Field acts as a validator, setting length constraints.
class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)

class GetTask(BaseModel):
    id: str
    title: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_completed: bool
    is_deleted: bool

class CreateTask(TaskBase):
    pass

class UpdateTask(BaseModel):
    title: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_completed: Optional[bool] = None


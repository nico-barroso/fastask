from pydantic import BaseModel, Field
from typing import Optional

# Base task model. The rest of the models inherit from this one.
# Field acts as a validator, setting length constraints.
class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)

class CreateTask(TaskBase):
    is_compleated : bool = False

class GetTask(TaskBase):
    id: int
    is_compleated : bool

class UpdateTask(BaseModel):
    title: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_compleated: Optional[bool] = None


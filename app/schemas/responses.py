from pydantic import BaseModel, Field
from typing import Optional

class ApiResponse[T](BaseModel):
    success: bool = Field(description="Indicates if the request was successful")
    message: str = Field(description="Human readable message")
    data: Optional[T] = Field(default=None, description="Response payload")
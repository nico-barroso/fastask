from pydantic import BaseModel
from typing import Optional

class ApiResponse[T](BaseModel):
    success: bool
    message: str
    data: Optional[T] = None
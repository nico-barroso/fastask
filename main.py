from fastapi import FastAPI
from routers import tasks, lists
from schemas.responses import ApiResponse

app = FastAPI(
    title="Task API",
    description="A simple task management API with soft delete, pagination, and UUID support.",
    version="1.0.0",
)

app.include_router(tasks.router)
app.include_router(lists.router)


@app.get(
        "/", response_model=ApiResponse[None], summary="Health check", tags=["root"])
async def root():
    """Check if the API is up and running."""
    return ApiResponse(success=True, message="Welcome, TaskApi is working!", data=None)

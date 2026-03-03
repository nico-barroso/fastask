from fastapi import FastAPI
from routers import tasks
from schemas.responses import ApiResponse

app = FastAPI()

app.include_router(tasks.router)

@app.get("/", response_model=ApiResponse)
async def root():
    return ApiResponse(success=True, message="Welcome, TaskApi is working!", data=None)

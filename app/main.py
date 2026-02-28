from fastapi import FastAPI
#from routers.tasks import tasks
from schemas.responses import ApiResponse

app = FastAPI()


@app.get("/", response_model=ApiResponse)
def root():
    return ApiResponse(success=True, message="Welcome, TaskApi is working!", data=None)

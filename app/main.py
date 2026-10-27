
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import InvalidTaskError, TaskNotFoundError
from app.routers.tasks import router as tasks_router

app = FastAPI(
    title="Task Tracker API",
    description="A REST API to create, manage, and track tasks.",
    version="0.1.0",
)


@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(
    request: Request,
    exc: TaskNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


@app.exception_handler(InvalidTaskError)
async def invalid_task_handler(
    request: Request,
    exc: InvalidTaskError,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
    )


app.include_router(tasks_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

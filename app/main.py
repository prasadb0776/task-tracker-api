from fastapi import FastAPI
from app.routers.tasks import router as tasks_router
app = FastAPI(
    title="Task Tracker API",
    description="A REST API to create, manage, and track tasks.",
    version="0.1.0",
)
app.include_router(tasks_router)

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
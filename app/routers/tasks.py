from datetime import date

from fastapi import APIRouter, HTTPException, Query, status
from app.schemas import (
    TaskCreate,
    TaskListResponse,
    TaskPriority,
    TaskResponse,
    TaskStatsResponse,
    TaskStatus,
    TaskUpdate,
)
from app import service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    return service.create_task(task)


@router.get("/stats", response_model=TaskStatsResponse)
def get_task_stats():
    return service.get_task_stats()


@router.get("", response_model=TaskListResponse)
def list_tasks(
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    priority: TaskPriority | None = None,
    q: str | None = None,
    due_before: date | None = None,
    overdue: bool = False,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    sort_by: str = "created_at",
    order: str = "desc",
    
):
    try:
        items, total = service.list_tasks(
            limit=limit,
            offset=offset,
            status=status_filter.value if status_filter else None,
            priority=priority.value if priority else None,
            q=q,
            due_before=due_before,
            overdue=overdue,
            sort_by=sort_by,
            order=order,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    return service.get_task(task_id)


@router.put("/{task_id}", response_model=TaskResponse)
def replace_task(task_id: int, task: TaskCreate):
    service.get_task(task_id)
    return service.update_task(
        task_id,
        TaskUpdate(**task.model_dump()),
    )


@router.patch("/{task_id}", response_model=TaskResponse)
def patch_task(task_id: int, updates: TaskUpdate):
    return service.update_task(task_id, updates)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    service.delete_task(task_id)
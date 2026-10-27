
from datetime import date

from fastapi import APIRouter, HTTPException, Query, status

from app.exceptions import InvalidTaskError, TaskNotFoundError
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
    try:
        return service.create_task(task)
    except InvalidTaskError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


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
    try:
        return service.get_task(task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{task_id}", response_model=TaskResponse)
def replace_task(task_id: int, task: TaskCreate):
    try:
        service.get_task(task_id)
        return service.update_task(
            task_id,
            TaskUpdate(**task.model_dump()),
        )
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidTaskError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.patch("/{task_id}", response_model=TaskResponse)
def patch_task(task_id: int, updates: TaskUpdate):
    try:
        return service.update_task(task_id, updates)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidTaskError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    try:
        service.delete_task(task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

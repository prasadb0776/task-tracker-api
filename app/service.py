
from datetime import date, datetime, timezone

from app import repository
from app.exceptions import InvalidTaskError, TaskNotFoundError
from app.schemas import TaskCreate, TaskUpdate


def utc_now() -> str:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()



def create_task(task: TaskCreate) -> dict:
    """Validate creation rules and create a task."""
    if task.due_date is not None and task.due_date < date.today():
        raise InvalidTaskError("Due date cannot be in the past")

    return repository.create_task(task)



def get_task(task_id: int) -> dict:
    """Return a task or raise an error if it does not exist."""
    task = repository.get_task_by_id(task_id)

    if task is None:
        raise TaskNotFoundError(f"Task {task_id} not found")

    return task


def update_task(task_id: int, updates: TaskUpdate) -> dict:
    """Apply business rules before updating a task."""
    existing = get_task(task_id)
    changes = updates.model_dump(exclude_unset=True)

    if not changes:
        raise InvalidTaskError("At least one field must be provided")

    if "title" in changes and changes["title"] is None:
        raise InvalidTaskError("Title cannot be null")

    if "status" in changes and changes["status"] is None:
        raise InvalidTaskError("Status cannot be null")

    if "priority" in changes and changes["priority"] is None:
        raise InvalidTaskError("Priority cannot be null")

    now = utc_now()
    changes["updated_at"] = now

    new_status = changes.get("status", existing["status"])
    if hasattr(new_status, "value"):
        new_status = new_status.value

    if new_status == "done":
        if existing["status"] != "done":
            changes["completed_at"] = now
    else:
        changes["completed_at"] = None

    updated = repository.update_task(task_id, changes)

    if updated is None:
        raise TaskNotFoundError(f"Task {task_id} not found")

    return updated


def delete_task(task_id: int) -> None:
    """Delete a task or raise an error if it does not exist."""
    if not repository.delete_task(task_id):
        raise TaskNotFoundError(f"Task {task_id} not found")


def list_tasks(**filters) -> tuple[list[dict], int]:
    """Delegate filtered listing to the repository."""
    return repository.list_tasks(**filters)


def get_task_stats() -> dict[str, int]:
    """Return aggregate task statistics."""
    return repository.get_task_stats()


from datetime import datetime, timezone,date
from app.database import get_connection
from app.schemas import TaskCreate


def utc_now() -> str:
    """Return the current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()

def create_task(task: TaskCreate) -> dict:
    """Insert a task into SQLite and return the created row."""
    now = utc_now()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tasks (
                title,
                description,
                status,
                priority,
                due_date,
                created_at,
                updated_at,
                completed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task.title,
                task.description,
                task.status.value,
                task.priority.value,
                task.due_date.isoformat() if task.due_date else None,
                now,
                now,
                now if task.status.value == "done" else None,
            ),
        )

        row = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

        return dict(row)


def get_task_by_id(task_id: int) -> dict | None:
    """Return a task by ID, or None if it does not exist."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        return dict(row) if row is not None else None

def list_tasks(
    limit: int = 20,
    offset: int = 0,
    status: str | None = None,
    priority: str | None = None,
    q: str | None = None,
    due_before: date | None = None,
    overdue: bool = False,
    sort_by: str = "created_at",
    order: str = "desc",
) -> tuple[list[dict], int]:
    """Return filtered tasks and the total matching count."""

    allowed_sort_columns = {
        "id": "id",
        "title": "title",
        "status": "status",
        "priority": "priority",
        "due_date": "due_date",
        "created_at": "created_at",
        "updated_at": "updated_at",
    }

    if sort_by not in allowed_sort_columns:
        raise ValueError("Invalid sort_by value")

    if order.lower() not in {"asc", "desc"}:
        raise ValueError("Invalid order value")

    conditions = []
    params = []

    if status is not None:
        conditions.append("status = ?")
        params.append(status)

    if priority is not None:
        conditions.append("priority = ?")
        params.append(priority)

    if q:
        conditions.append("(title LIKE ? OR description LIKE ?)")
        search = f"%{q}%"
        params.extend([search, search])

    if due_before is not None:
        conditions.append("due_date <= ?")
        params.append(due_before.isoformat())

    if overdue:
        conditions.append(
            "due_date < ? AND status != 'done'"
        )
        params.append(date.today().isoformat())

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    sort_column = allowed_sort_columns[sort_by]
    sort_order = order.upper()

    with get_connection() as connection:
        total = connection.execute(
            f"SELECT COUNT(*) FROM tasks {where_clause}",
            params,
        ).fetchone()[0]

        rows = connection.execute(
            f"""
            SELECT *
            FROM tasks
            {where_clause}
            ORDER BY {sort_column} {sort_order}
            LIMIT ? OFFSET ?
            """,
            (*params, limit, offset),
        ).fetchall()

        return [dict(row) for row in rows], total


def update_task(task_id: int, updates: dict) -> dict | None:
    """Update supplied task fields and return the updated task."""
    if not updates:
        updates = updates.copy()
        return get_task_by_id(task_id)

    allowed_fields = {
        "title",
        "description",
        "status",
        "priority",
        "due_date",
        "updated_at",
        "completed_at",
    }

    if not set(updates).issubset(allowed_fields):
        raise ValueError("Invalid update field")

    if "due_date" in updates and isinstance(updates["due_date"], date):
        updates["due_date"] = updates["due_date"].isoformat()

    for field in ("status", "priority"):
        value = updates.get(field)
        if hasattr(value, "value"):
            updates[field] = value.value

    fields = list(updates)
    assignments = ", ".join(f"{field} = ?" for field in fields)
    values = [updates[field] for field in fields]

    with get_connection() as connection:
        cursor = connection.execute(
            f"UPDATE tasks SET {assignments} WHERE id = ?",
            (*values, task_id),
        )

        if cursor.rowcount == 0:
            return None

        row = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        return dict(row) if row is not None else None


def delete_task(task_id: int) -> bool:
    """Delete a task; return True if a task was deleted."""
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,),
        )
        return cursor.rowcount > 0



def get_task_stats() -> dict[str, int]:
    """Return task counts by status and the number of overdue tasks."""
    today = date.today().isoformat()

    with get_connection() as connection:
        row = connection.execute(
            """SELECT
                COUNT(*) AS total,
                COALESCE(
                    SUM(CASE WHEN status = 'todo' THEN 1 ELSE 0 END), 0
                ) AS todo,
                COALESCE(
                    SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END), 0
                ) AS in_progress,
                COALESCE(
                    SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END), 0
                ) AS done,
                COALESCE(
                    SUM(
                        CASE
                            WHEN due_date < ? AND status != 'done'
                            THEN 1
                            ELSE 0
                        END
                    ), 0
                ) AS overdue
                FROM tasks""",
            (today,),
        ).fetchone()

        return {
            "total": row["total"],
            "todo": row["todo"],
            "in_progress": row["in_progress"],
            "done": row["done"],
            "overdue": row["overdue"],
        }

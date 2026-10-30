import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

from app.config import DATABASE_PATH

_TEST_DATABASE_PATH = None


def get_connection(db_path=None) -> sqlite3.Connection:
    path = (
        db_path
        if db_path is not None
        else _TEST_DATABASE_PATH
        if _TEST_DATABASE_PATH is not None
        else DATABASE_PATH
    )

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection



@contextmanager
def database_connection(db_path=None) -> Iterator[sqlite3.Connection]:
    """Provide a SQLite connection and always close it."""
    connection = get_connection(db_path)

    try:
        with connection:
            yield connection
    finally:
        connection.close()

def init_db(db_path=None) -> None:
    """Create the tasks table and indexes if they don't exist."""
    with database_connection(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL
                    CHECK (length(trim(title)) BETWEEN 1 AND 100),
                description TEXT
                    CHECK (
                        description IS NULL
                        OR length(description) <= 1000
                    ),
                status TEXT NOT NULL DEFAULT 'todo'
                    CHECK (
                        status IN ('todo', 'in_progress', 'done')
                    ),
                priority TEXT NOT NULL DEFAULT 'medium'
                    CHECK (
                        priority IN ('low', 'medium', 'high')
                    ),
                due_date TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                completed_at TEXT
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_tasks_status
            ON tasks(status)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_tasks_priority
            ON tasks(priority)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_tasks_due_date
            ON tasks(due_date)
            """
        )

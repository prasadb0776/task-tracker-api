import sqlite3

import pytest

from app.database import database_connection


def test_database_connection_closes_after_exception(tmp_path):
    db_path = tmp_path / "connection_test.db"
    connection = None

    with pytest.raises(RuntimeError, match="simulated failure"):
        with database_connection(str(db_path)) as connection:
            connection.execute("CREATE TABLE example (id INTEGER)")
            raise RuntimeError("simulated failure")

    assert connection is not None

    with pytest.raises(sqlite3.ProgrammingError, match="closed database"):
        connection.execute("SELECT 1")
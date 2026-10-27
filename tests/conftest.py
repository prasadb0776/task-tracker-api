import pytest
from fastapi.testclient import TestClient

from app import database
from app.database import init_db
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "test_tasks.db"

    monkeypatch.setattr(database, "_TEST_DATABASE_PATH", str(test_db))
    init_db(str(test_db))

    with TestClient(app) as test_client:
        yield test_client

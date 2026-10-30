from fastapi.testclient import TestClient

from app import database
from app.main import app


def test_startup_creates_table_on_fresh_database(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "_TEST_DATABASE_PATH", str(tmp_path / "fresh.db"))

    with TestClient(app) as test_client:  # context manager runs startup
        response = test_client.post("/tasks", json={"title": "First task"})

    assert response.status_code == 201
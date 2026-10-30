from fastapi.testclient import TestClient

from app import service
from app.main import app


def test_unexpected_error_returns_clean_500(client, monkeypatch):
    def boom():
        raise RuntimeError("secret internal detail")

    monkeypatch.setattr(service, "get_task_stats", boom)

    with TestClient(app, raise_server_exceptions=False) as test_client:
        response = test_client.get("/tasks/stats")

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    assert "secret" not in response.text
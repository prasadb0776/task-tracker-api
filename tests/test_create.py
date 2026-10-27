
def test_create_task_success(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Learn pytest",
            "description": "Write my first API test",
            "priority": "high",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Learn pytest"
    assert data["description"] == "Write my first API test"
    assert data["status"] == "todo"
    assert data["priority"] == "high"
    assert data["id"] > 0
    assert data["completed_at"] is None


def test_create_task_trims_title(client):
    response = client.post(
        "/tasks",
        json={"title": "  Learn FastAPI  "},
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Learn FastAPI"


def test_create_task_rejects_empty_title(client):
    response = client.post(
        "/tasks",
        json={"title": "   "},
    )

    assert response.status_code == 422


def test_create_task_rejects_invalid_priority(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Test invalid priority",
            "priority": "urgent",
        },
    )

    assert response.status_code == 422

def test_create_task_rejects_server_managed_fields(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Test task",
            "id": 999,
            "created_at": "2026-01-01T00:00:00+00:00",
        },
    )

    assert response.status_code == 422


def test_create_task_rejects_missing_title(client):
    response = client.post(
        "/tasks",
        json={"description": "A task without a title"},
    )

    assert response.status_code == 422


def test_create_task_rejects_whitespace_only_title(client):
    response = client.post(
        "/tasks",
        json={"title": "   "},
    )

    assert response.status_code == 422


def test_create_task_rejects_invalid_due_date(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Invalid date task",
            "due_date": "not-a-date",
        },
    )

    assert response.status_code == 422


def test_list_tasks_returns_created_tasks(client):
    client.post("/tasks", json={"title": "Task A"})
    client.post("/tasks", json={"title": "Task B"})

    response = client.get("/tasks")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_filter_tasks_by_status(client):
    client.post("/tasks", json={"title": "Todo task"})
    client.post(
        "/tasks",
        json={"title": "Completed task", "status": "done"},
    )

    response = client.get("/tasks", params={"status": "done"})

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Completed task"


def test_search_tasks(client):
    client.post(
        "/tasks",
        json={"title": "Learn repository pattern"},
    )
    client.post("/tasks", json={"title": "Learn FastAPI"})

    response = client.get("/tasks", params={"q": "repository"})

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Learn repository pattern"


def test_list_tasks_pagination(client):
    for title in ["Task A", "Task B", "Task C"]:
        client.post("/tasks", json={"title": title})

    response = client.get(
        "/tasks",
        params={"limit": 2, "offset": 0},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 3
    assert data["limit"] == 2
    assert data["offset"] == 0


def test_list_tasks_rejects_limit_above_maximum(client):
    response = client.get("/tasks", params={"limit": 200})

    assert response.status_code == 422


def test_list_tasks_rejects_invalid_status(client):
    response = client.get("/tasks?status=waiting")

    assert response.status_code == 422


def test_list_tasks_rejects_invalid_priority(client):
    response = client.get("/tasks?priority=urgent")

    assert response.status_code == 422


def test_list_tasks_rejects_zero_limit(client):
    response = client.get("/tasks?limit=0")

    assert response.status_code == 422


def test_list_tasks_rejects_negative_offset(client):
    response = client.get("/tasks?offset=-1")

    assert response.status_code == 422


def test_list_tasks_rejects_invalid_sort_by(client):
    response = client.get("/tasks?sort_by=invalid_column")

    assert response.status_code == 422


def test_list_tasks_rejects_invalid_order(client):
    response = client.get("/tasks?order=sideways")

    assert response.status_code == 422

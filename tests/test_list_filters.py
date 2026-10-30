
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


from datetime import date, timedelta


def test_filter_tasks_by_priority(client):
    client.post("/tasks", json={"title": "Low one", "priority": "low"})
    client.post("/tasks", json={"title": "High one", "priority": "high"})
    data = client.get("/tasks", params={"priority": "high"}).json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "High one"


def test_sort_by_priority_uses_priority_order(client):
    for title, priority in [("A", "low"), ("B", "high"), ("C", "medium")]:
        client.post("/tasks", json={"title": title, "priority": priority})
    data = client.get(
        "/tasks", params={"sort_by": "priority", "order": "desc"}
    ).json()
    assert [t["priority"] for t in data["items"]] == ["high", "medium", "low"]


def test_sort_by_created_at_ascending(client):
    for title in ["First", "Second", "Third"]:
        client.post("/tasks", json={"title": title})
    data = client.get(
        "/tasks", params={"sort_by": "created_at", "order": "asc"}
    ).json()
    assert [t["title"] for t in data["items"]] == ["First", "Second", "Third"]


def test_overdue_filter_excludes_done_and_undated_tasks(client):
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    overdue = client.post("/tasks", json={"title": "Overdue"}).json()
    finished = client.post(
        "/tasks", json={"title": "Done late", "status": "done"}
    ).json()
    client.post("/tasks", json={"title": "No due date"})
    for task in (overdue, finished):
        client.patch(f"/tasks/{task['id']}", json={"due_date": yesterday})

    data = client.get("/tasks", params={"overdue": "true"}).json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Overdue"


def test_due_before_filter(client):
    soon = (date.today() + timedelta(days=2)).isoformat()
    later = (date.today() + timedelta(days=30)).isoformat()
    client.post("/tasks", json={"title": "Soon", "due_date": soon})
    client.post("/tasks", json={"title": "Later", "due_date": later})
    cutoff = (date.today() + timedelta(days=7)).isoformat()
    data = client.get("/tasks", params={"due_before": cutoff}).json()
    assert [t["title"] for t in data["items"]] == ["Soon"]

def test_sort_by_priority_ascending(client):
    for title, priority in [("A", "high"), ("B", "low"), ("C", "medium")]:
        client.post("/tasks", json={"title": title, "priority": priority})
    data = client.get(
        "/tasks", params={"sort_by": "priority", "order": "asc"}
    ).json()
    assert [t["priority"] for t in data["items"]] == ["low", "medium", "high"]

from datetime import date, timedelta


def test_stats_for_empty_database(client):
    response = client.get("/tasks/stats")

    assert response.status_code == 200
    assert response.json() == {
        "total": 0,
        "todo": 0,
        "in_progress": 0,
        "done": 0,
        "overdue": 0,
    }


def test_stats_count_tasks_by_status(client):
    client.post("/tasks", json={"title": "Todo task"})
    client.post(
        "/tasks",
        json={"title": "Active task", "status": "in_progress"},
    )
    client.post(
        "/tasks",
        json={"title": "Finished task", "status": "done"},
    )

    response = client.get("/tasks/stats")

    assert response.status_code == 200
    assert response.json() == {
        "total": 3,
        "todo": 1,
        "in_progress": 1,
        "done": 1,
        "overdue": 0,
    }


def test_stats_count_overdue_tasks(client):
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    todo = client.post(
        "/tasks",
        json={"title": "Overdue todo"},
    ).json()

    active = client.post(
        "/tasks",
        json={"title": "Overdue active", "status": "in_progress"},
    ).json()

    completed = client.post(
        "/tasks",
        json={"title": "Completed task", "status": "done"},
    ).json()

    # Set past due dates after creation.
    for task in (todo, active, completed):
        response = client.patch(
            f"/tasks/{task['id']}",
            json={"due_date": yesterday},
        )
        assert response.status_code == 200

    response = client.get("/tasks/stats")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["todo"] == 1
    assert data["in_progress"] == 1
    assert data["done"] == 1
    assert data["overdue"] == 2

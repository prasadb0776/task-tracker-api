
def test_delete_task_success(client):
    created = client.post(
        "/tasks",
        json={"title": "Task to delete"},
    ).json()

    response = client.delete(f"/tasks/{created['id']}")

    assert response.status_code == 204
    assert response.content == b""

    get_response = client.get(f"/tasks/{created['id']}")
    assert get_response.status_code == 404


def test_delete_missing_task_returns_404(client):
    response = client.delete("/tasks/9999")

    assert response.status_code == 404


def test_deleted_task_is_removed_from_list(client):
    created = client.post(
        "/tasks",
        json={"title": "Temporary task"},
    ).json()

    client.delete(f"/tasks/{created['id']}")

    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json()["total"] == 0
    assert response.json()["items"] == []

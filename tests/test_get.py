def test_get_existing_task(client):
    created = client.post("/tasks", json={"title": "Find me"}).json()
    response = client.get(f"/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.json() == created


def test_get_missing_task_returns_404(client):
    assert client.get("/tasks/9999").status_code == 404


def test_get_task_with_invalid_id_returns_422(client):
    assert client.get("/tasks/abc").status_code == 422
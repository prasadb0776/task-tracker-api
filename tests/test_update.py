
def test_patch_task_title(client):
    created = client.post(
        "/tasks",
        json={"title": "Original title"},
    ).json()

    response = client.patch(
        f"/tasks/{created['id']}",
        json={"title": "Updated title"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated title"


def test_completing_task_sets_completed_at(client):
    created = client.post(
        "/tasks",
        json={"title": "Finish testing"},
    ).json()

    response = client.patch(
        f"/tasks/{created['id']}",
        json={"status": "done"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "done"
    assert data["completed_at"] is not None


def test_reopening_task_clears_completed_at(client):
    created = client.post(
        "/tasks",
        json={"title": "Complete and reopen"},
    ).json()

    completed = client.patch(
        f"/tasks/{created['id']}",
        json={"status": "done"},
    )
    assert completed.status_code == 200
    assert completed.json()["completed_at"] is not None

    reopened = client.patch(
        f"/tasks/{created['id']}",
        json={"status": "todo"},
    )

    assert reopened.status_code == 200
    assert reopened.json()["status"] == "todo"
    assert reopened.json()["completed_at"] is None


def test_patch_empty_body_is_rejected(client):
    created = client.post(
        "/tasks",
        json={"title": "Test empty patch"},
    ).json()

    response = client.patch(f"/tasks/{created['id']}", json={})

    assert response.status_code == 422


def test_patch_missing_task_returns_404(client):
    response = client.patch(
        "/tasks/9999",
        json={"title": "Does not exist"},
    )

    assert response.status_code == 404


def test_put_replaces_task_fields(client):
    created = client.post(
        "/tasks",
        json={
            "title": "Old title",
            "description": "Old description",
            "priority": "low",
        },
    ).json()

    response = client.put(
        f"/tasks/{created['id']}",
        json={
            "title": "Replacement title",
            "description": "New description",
            "priority": "high",
            "status": "todo",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Replacement title"
    assert data["description"] == "New description"
    assert data["priority"] == "high"


def test_put_resets_omitted_fields_to_defaults(client):
    created = client.post(
        "/tasks",
        json={
            "title": "Original task",
            "description": "Original description",
            "status": "in_progress",
            "priority": "high",
        },
    )
    task_id = created.json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        json={"title": "Replaced task"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Replaced task"
    assert data["description"] is None
    assert data["status"] == "todo"
    assert data["priority"] == "medium"


def test_patch_task_with_invalid_id_returns_422(client):
    response = client.patch(
        "/tasks/abc",
        json={"title": "Updated title"},
    )

    assert response.status_code == 422

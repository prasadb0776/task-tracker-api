
# Task Tracker API

A REST API for creating, managing, filtering, and tracking tasks, built with FastAPI, Pydantic, and SQLite.

## Features

- Create, retrieve, update, and delete tasks
- Validate task titles, descriptions, status, and priority
- Filter and search tasks
- Sort and paginate task lists
- Track completed and overdue tasks
- View task statistics
- Automated tests using pytest and a temporary SQLite database

## Tech Stack

- Python 3.10+
- FastAPI
- Pydantic v2
- SQLite (`sqlite3`)
- Uvicorn
- Pytest

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run the API

```bash
uvicorn app.main:app --reload
```

Interactive API documentation:

http://127.0.0.1:8000/docs

Health check:

http://127.0.0.1:8000/health

## Run Tests

```bash
python -m pytest -v
```

Tests use an isolated temporary SQLite database.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/tasks` | Create a task |
| GET | `/tasks` | List, filter, search, sort, and paginate tasks |
| GET | `/tasks/stats` | Retrieve task statistics |
| GET | `/tasks/{task_id}` | Retrieve a task |
| PUT | `/tasks/{task_id}` | Replace editable task fields |
| PATCH | `/tasks/{task_id}` | Update selected fields |
| DELETE | `/tasks/{task_id}` | Delete a task |

## Task Fields

- `title`: Required, 1–100 characters
- `description`: Optional, up to 1000 characters
- `status`: `todo`, `in_progress`, or `done`
- `priority`: `low`, `medium`, or `high`
- `due_date`: Optional due date

Creation, update, and completion timestamps are managed by the API.

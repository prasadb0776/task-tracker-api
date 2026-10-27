import importlib

import pytest

from app import config


@pytest.fixture
def reload_config():
    original_path = config.DATABASE_PATH

    yield

    importlib.reload(config)
    config.DATABASE_PATH = original_path


def test_database_path_uses_environment_variable(
    monkeypatch,
    reload_config,
):
    monkeypatch.setenv("DATABASE_PATH", "/tmp/custom_tasks.db")

    importlib.reload(config)

    assert config.DATABASE_PATH == "/tmp/custom_tasks.db"


def test_database_path_defaults_when_environment_variable_is_missing(
    monkeypatch,
    reload_config,
):
    monkeypatch.delenv("DATABASE_PATH", raising=False)

    importlib.reload(config)

    assert config.DATABASE_PATH == "tasks.db"
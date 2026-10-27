#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

env -u PYTHONPATH PYTHONNOUSERSITE=1 \
    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
    python -m pytest -q

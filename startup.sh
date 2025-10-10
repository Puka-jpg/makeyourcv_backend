#!/bin/bash

set -e

APP_DIR="/var/www/resume-builder-fastapi"
UV="$HOME/.local/bin/uv"
PIDS=()

# Clean up
cleanup() {
    echo "[INFO] Stopping all processes..."
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    exit 0
}

trap cleanup EXIT INT TERM


# Build service
cd $APP_DIR

$UV sync --frozen

$UV run alembic upgrade head

$APP_DIR/.venv/bin/gunicorn &
PIDS+=($!)

wait || true
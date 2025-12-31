default:
    @just --list

help:
    @echo
    @echo "install                  -- install backend dependencies"
    @echo "format                   -- format backend"
    @echo "lint                     -- lint backend"
    @echo "mypy                     -- type check backend"
    @echo "spellcheck               -- spell check"
    @echo "test                     -- test backend"
    @echo "dev                      -- start backend development server"
    @echo "generate-configs         -- generate deployment configs"
    @echo "clean                    -- remove backend containers and volumes"
    @echo "clean-test               -- remove test containers and volumes"
    @echo

install:
    uv sync --frozen

lint:
    uv run ruff check .

mypy:
    uv run mypy .

format:
    uv run ruff check --fix .
    uv run ruff format .

spellcheck:
    uv run codespell --skip="*.git,*.json,package-lock.json" .

test:
    ENV_FILE=.env.test uv run pytest

dev:
    uv run uvicorn main:app \
        --reload \
        --host 127.0.0.1 \
        --port 8080 \
        --workers 1 \
        --log-level info

migrate:
    uv run alembic upgrade head


generate-configs:
    uv run generate_configs.py

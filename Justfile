default:
    @just --list

help:
    @echo
    @echo "Backend Commands:"
    @echo "  install                  -- install backend dependencies (uv)"
    @echo "  format                   -- format backend code"
    @echo "  lint                     -- lint backend code"
    @echo "  test                     -- run backend tests"
    @echo "  dev                      -- start backend API server (fastapi)"
    @echo
    @echo "Agent Commands:"
    @echo "  agent-dev                -- run agent in CLI mode"
    @echo "  agent-server             -- run agent WebSocket server (port 8000)"
    @echo
    @echo "Frontend Commands:"
    @echo "  frontend-install         -- install frontend dependencies (npm)"
    @echo "  frontend-dev             -- start frontend dev server (next.js)"
    @echo

# --- Backend ---

install:
    cd backend && uv sync --frozen

lint:
    cd backend && uv run ruff check .

mypy:
    cd backend && uv run mypy .

format:
    cd backend && uv run ruff check --fix .
    cd backend && uv run ruff format .

pyright:
    cd backend && uv run pyright .

spellcheck:
    cd backend && uv run codespell --skip="*.git,*.json,package-lock.json" .

test:
    cd backend && ENV_FILE=.env.test uv run pytest

dev:
    cd backend && uv run uvicorn main:app \
        --reload \
        --host 127.0.0.1 \
        --port 8080 \
        --workers 1 \
        --log-level info

migrate:
    cd backend && uv run alembic upgrade head

generate-configs:
    cd backend && uv run generate_configs.py

clean:
    @echo "Clean not implemented for local dev yet"

clean-test:
    @echo "Clean-test not implemented for local dev yet"

# --- Agent ---

agent-dev:
    cd backend && PYTHONPATH=.. uv run ../agent/main.py

agent-server:
    cd backend && PYTHONPATH=.. PORT=8005 uv run python ../agent/server.py

# --- Frontend ---

frontend-install:
    cd frontend/makeyourcvfrontend && npm install

frontend-dev:
    cd frontend/makeyourcvfrontend && npm run dev

help:
	@echo
	@echo "install                  -- install backend dependencies"
	@echo "format                   -- format backend"
	@echo "lint                     -- lint backend"
	@echo "mypy                     -- type check backend"
	@echo "dev                      -- start backend development server"
	@echo


.PHONY: install lint mypy format

install:
	uv sync --frozen

lint:
	uv run ruff check .

mypy:
	uv run mypy .

format:
	uv run ruff check --fix .
	uv run ruff format .

.PHONY: dev
dev:
	uv run uvicorn main:app --reload --host "127.0.0.1" --port 8080 --workers 1 --log-level info
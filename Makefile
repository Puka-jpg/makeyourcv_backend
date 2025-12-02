help:
	@echo
	@echo "install                  -- install backend dependencies"
	@echo "format                   -- format backend"
	@echo "lint                     -- lint backend"
	@echo "mypy                     -- type check backend"
	@echo "spellcheck                    -- spell check "
	@echo "test                     -- test backend"
	@echo "dev                      -- start backend development server"
	@echo "generate-configs         -- generate deployment configs"
	@echo "clean                    -- remove backend containers and volumns"
	@echo "clean-test               -- remove test containers and volumns"
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

.PHONY: spellcheck
spellcheck:
	uv run codespell --skip="*.git,*.json,package-lock.json" .

.PHONY: test
test:
	docker compose -f docker-compose.test.yml up -d
	@echo "Waiting 5 seconds for docker services to be healthy..."
	@sleep 5
	ENV_FILE=.env.test uv run pytest

.PHONY: dev
dev:
	docker compose up -d
	@echo "Waiting 5 seconds for docker services to be healthy..."
	@sleep 5
	uv run uvicorn main:app --reload --host "127.0.0.1" --port 8080 --workers 1 --log-level info

.PHONY: migrate
migrate:
	uv run alembic upgrade head

.PHONY: clean
clean:
	docker compose down -v

.PHONY: clean-test
clean-test:
	docker compose -f docker-compose.test.yml down -v

.PHONY: generate-configs
generate-configs:
	uv run generate_configs.py
Creating migration file
Run following command to generate migration file

uv run alembic revision --autogenerate -m <meaningful-migration-name>
Applying the migration

uv run alembic upgrade head
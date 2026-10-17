.PHONY: dev test lint fmt migrate migrate-down
dev:
	uv run uvicorn echovault.main:app --reload
test:
	uv run pytest
lint:
	uv run ruff check . && uv run mypy src tests
fmt:
	uv run ruff format . && uv run ruff check --fix .
migrate:
	uv run alembic upgrade head
migrate-down:
	uv run alembic downgrade -1

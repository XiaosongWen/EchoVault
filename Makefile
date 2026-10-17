.PHONY: dev test lint fmt
dev:
	uv run uvicorn echovault.main:app --reload
test:
	uv run pytest
lint:
	uv run ruff check . && uv run mypy src
fmt:
	uv run ruff format . && uv run ruff check --fix .

# EchoVault

Centralized cross-device memory hub: FastAPI REST (`/api/v1`) + FastMCP (`/mcp`) over Supabase PostgreSQL.

## Layout
```
docs/        PRD, backend design, task backlog
tasks/       one file per task (TASK-01..16), track status here
src/echovault/
  api/v1/    REST routers      mcp/      FastMCP tools
  core/      auth, errors, logging   services/  business logic (shared by REST + MCP)
  db/        models, sessions  workers/  ingestion & extraction workers
  schemas/   Pydantic models
migrations/  Alembic          tests/    unit + integration
deploy/      Cloud Run config
```

## Dev
```
uv sync
cp .env.example .env
make dev     # http://localhost:8000/health
make test
```

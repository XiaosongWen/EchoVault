FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock* README.md ./
COPY src ./src
RUN uv sync --no-dev
CMD ["sh", "-c", "uv run uvicorn echovault.main:app --host 0.0.0.0 --port ${PORT:-8080}"]

FROM python:3.11-slim-bookworm AS base

# PYTHONPATH=/app is required so "from backend..." imports resolve —
# the backend source is copied to /app/backend below.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    UV_PROJECT_ENVIRONMENT=/usr/local \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.12.12 /uv /uvx /bin/

# Dependencies layer, kept separate so it's cached until pyproject/uv.lock change
COPY pyproject.toml uv.lock ./backend/
RUN uv sync --project backend --frozen --no-install-project

# Source code (build context is src/backend/, copied under backend so the
# "backend.*" import path resolves inside the container)
COPY . ./backend
RUN chmod +x ./backend/entrypoint.sh

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# No EXPOSE — the port is runtime-only (see entrypoint.sh); EXPOSE can't take
# a runtime value, so baking one in here would just be a stale default.

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f "http://localhost:${PORT:-8000}/api/v1/health/live" || exit 1

ENTRYPOINT ["./backend/entrypoint.sh"]

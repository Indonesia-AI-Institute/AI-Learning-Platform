#!/bin/sh
set -e

echo "Running database migrations..."
alembic -c backend/alembic.ini upgrade head

echo "Starting API server..."
exec uvicorn backend.main:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8000}"

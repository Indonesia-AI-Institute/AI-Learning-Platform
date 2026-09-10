---
name: dev-server
description: Start the AI Learning Platform backend locally for development — verifies/creates .env.be, applies pending Alembic migrations, then runs uvicorn with reload using the correct PYTHONPATH so "backend.*" imports resolve. Use when asked to run, start, or serve the backend outside Docker.
---

# Backend dev server

Runs the FastAPI backend locally (not via Docker) with hot reload, for
active development.

## Steps

1. **Confirm working directory context.** All commands below assume the
   repo root as the reference point; the backend project itself lives at
   `src/backend/`.

2. **Ensure `.env.be` exists** at the repo root. If it's missing, copy
   `.env.be.example` to `.env.be` and tell the user which required values
   (`SECRET_KEY`, `CORS_ORIGINS`, `DATABASE_URL`, and an LLM provider key)
   need filling in before the server will start — don't guess values for
   secrets. If `DATABASE_URL` still says `@db:` (the Docker service name),
   flag that it likely needs to be `@localhost:` for a non-Docker run.

3. **Confirm Postgres is reachable** at whatever `DATABASE_URL` in
   `.env.be` resolves to. If not, tell the user rather than silently
   trying to start a database for them — they may already have one
   running elsewhere, or want to point at a Docker container themselves.

4. **Sync dependencies** (idempotent, safe to always run):
   ```bash
   cd src/backend && uv sync --extra dev
   ```

5. **Apply migrations:**
   ```bash
   cd src/backend && uv run alembic upgrade head
   ```
   If this fails, stop and report the error — don't proceed to start a
   server against a schema that might be out of date.

6. **Start the server**, run from the repo root with `PYTHONPATH=src` set
   (required — see `CLAUDE.md` "Critical rule #1": the package root is
   `src/backend/` itself, so `src/` must be on the path for
   `backend.main` to import):
   ```bash
   PYTHONPATH="$(pwd)/src" uv run --project src/backend uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```
   Run this in the background (or foreground per the user's stated
   preference) — it's a long-running process, not a one-shot command.

7. **Report back**: the URL (`http://localhost:8000`), that interactive
   docs are at `/docs`, and how to stop it (Ctrl+C, or note the background
   task if launched that way).

## If it fails to start

- `ModuleNotFoundError: No module named 'backend'` → `PYTHONPATH` wasn't
  set, or the command was run from inside `src/backend/` instead of the
  repo root. Re-run exactly as in step 6.
- `pydantic_core._pydantic_core.ValidationError: SECRET_KEY` /
  `CORS_ORIGINS` → one of those is missing or invalid in `.env.be`. Both
  are required with no usable default, on purpose (see `CLAUDE.md`).
- A connection error to Postgres → `DATABASE_URL` in `.env.be` doesn't
  point at a reachable database. Don't silently switch to a different
  database; surface the actual connection error to the user.

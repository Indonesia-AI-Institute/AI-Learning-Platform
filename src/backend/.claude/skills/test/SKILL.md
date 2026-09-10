---
name: test
description: Run the AI Learning Platform backend's pytest suite (unit and/or integration), handling the disposable Postgres test container that integration tests need. Use when asked to run backend tests, check if backend changes broke anything, or verify a fix with the test suite.
---

# Backend test suite

`tests/unit/` needs no database at all. `tests/integration/` needs a real
Postgres reachable at `DATABASE_URL` (default:
`postgresql+asyncpg://test:test@localhost:5433/test`) — SQLite can't run
the `sqlalchemy.dialects.postgresql.UUID` type the models use. Every
integration test run **drops and recreates the entire schema**, so never
point it at a database anyone cares about.

## Steps

1. **Decide scope.** If the user just asked to "run the tests" with no
   qualifier, run everything. If they're iterating on a pure-logic change
   (schemas, auth primitives, agent prompt logic, the banlist filter),
   `tests/unit/` alone is enough and much faster — no container needed.

2. **For unit-only runs**, skip straight to step 5 — no database setup
   needed. Verify this is actually true by checking there's no `db_session`
   or `client` fixture usage creeping into `tests/unit/` (there shouldn't
   be; that's what `tests/integration/` is for).

3. **For integration or full runs, get a test Postgres up.** Check
   whether something is already listening on the target `DATABASE_URL`'s
   port before starting a new one — if so, reuse it rather than starting
   a duplicate.

   Otherwise, confirm a Docker daemon is reachable (`docker info`). If
   not and the machine uses Colima (macOS without Docker Desktop is the
   common case), check `colima list` for an existing profile and start
   that one — don't invent a new profile name; ask the user which to use
   if none exists yet. Once a daemon is reachable:
   ```bash
   docker run -d --rm --name pg-test -p 5433:5432 \
     -e POSTGRES_USER=test -e POSTGRES_PASSWORD=test -e POSTGRES_DB=test \
     postgres:15-alpine
   ```
   Wait for readiness rather than a fixed sleep:
   ```bash
   until docker exec pg-test pg_isready -U test -d test; do sleep 1; done
   ```

4. **Sync dev dependencies** if not already done:
   ```bash
   cd src/backend && uv sync --extra dev
   ```

5. **Run pytest from the repo root**, with `PYTHONPATH=src` (required for
   `backend.*` imports to resolve — see `CLAUDE.md`):
   ```bash
   PYTHONPATH="$(pwd)/src" uv run --project src/backend pytest src/backend/tests -q
   # or narrower: .../tests/unit, .../tests/integration, or a specific file
   ```

6. **Report results plainly**: pass/fail counts, and for any failure the
   actual assertion/traceback — don't summarize a failure away as
   "probably fine." If a test that used to pass now fails, that's a real
   regression to investigate, not a formatting issue.

7. **Clean up** what this skill started (and nothing the user was
   already running before it):
   ```bash
   docker stop pg-test
   ```
   If a Colima VM (or any Docker daemon) was already running before this
   skill touched anything, leave it running — only stop a VM this skill
   itself started.

## Notes

- Don't invent a different test database strategy (SQLite, mocking the
  DB session, etc.) to avoid needing Postgres — the whole point of
  `tests/integration/` is exercising the real dialect-specific behavior,
  and past IDOR bugs here were only caught by tests that hit a real
  database with real cross-tenant data.
- If you're verifying a specific bug fix, prefer running just the
  relevant test file/test rather than the whole suite for a fast
  iteration loop, then run the full suite once before calling it done.

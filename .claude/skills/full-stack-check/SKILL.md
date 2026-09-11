---
name: full-stack-check
description: Run both projects' comprehensive checks (backend pytest, frontend lint/build/test) and report one consolidated pass/fail summary. Use when asked to check, verify, or validate the whole repo before pushing or opening a PR that touches both backend and frontend, or when unsure which side a change affected.
---

# Full-stack check

Runs each project's own comprehensive check and merges the results into
one report. This is a thin wrapper — the actual logic lives in each
project's own `check`/`test` skill; read those (or `src/backend/CLAUDE.md`
/ `src/frontend/CLAUDE.md`'s "Testing" sections) for what each step
actually does and how to debug a failure.

## When to use this vs. the per-project skills

If a change only touched `src/frontend/` or only `src/backend/`, just run
that project's own `check`/`test` skill directly — running both wastes a
Postgres container spin-up for a change that couldn't have affected the
backend. Use this skill specifically when a change touches both sides
(a new endpoint plus the frontend code that calls it, a shared env var,
anything in the root-level compose/deploy files), or when kicking off a
final check before opening a PR and it's not worth reasoning about which
side is actually affected.

## Steps

1. **Backend**: get a disposable Postgres up if one isn't already
   reachable, then run the full suite. This is exactly the backend's own
   `test` skill — follow it for the container lifecycle (start, wait for
   `pg_isready`, run pytest, stop only if this skill started it):
   ```bash
   docker run -d --rm --name pg-test -p 5433:5432 \
     -e POSTGRES_USER=test -e POSTGRES_PASSWORD=test -e POSTGRES_DB=test \
     postgres:15-alpine
   until docker exec pg-test pg_isready -U test -d test; do sleep 1; done

   cd src/backend && uv sync --extra dev && cd ../..
   PYTHONPATH="$(pwd)/src" uv run --project src/backend pytest src/backend/tests -q
   ```

2. **Frontend**: this project's own `check` skill — lint, build, test:
   ```bash
   cd src/frontend
   bun install
   bun run lint
   bun run build
   bun test
   cd ..
   ```

3. **Clean up** anything this skill started (the `pg-test` container) —
   but leave any Docker daemon or Colima VM running if it was already up
   before this skill touched anything:
   ```bash
   docker stop pg-test
   ```

4. **Report one consolidated summary**: pass/fail for each of the four
   checks (pytest, lint, build, bun test), and for any failure, the
   actual error output attributed to which side it came from. Don't
   collapse "3 of 4 passed" into a vague "mostly good" — a reader needs
   to know exactly what's still broken and where.

## Notes

- Run the backend and frontend checks independently of each other's
  outcome — a backend test failure is not a reason to skip running the
  frontend checks too. Gather the full picture before reporting, don't
  stop at the first red result.
- If both sides are clean, say so plainly. This skill exists to save the
  back-and-forth of running each project's checks separately, not to
  produce a longer report than a plain "all clean" would be.

---
name: check
description: Run the backend's full comprehensive check — ruff lint, ruff format check, and the full pytest suite — with a consolidated pass/fail report. Use when asked to do a final check, comprehensive check, or full verification of the backend, before considering a change done, or before committing/opening a PR.
---

# Backend comprehensive check

Three checks, each catching something the others don't: ruff's lint
rules catch unused imports/undefined names/common correctness footguns
statically, `ruff format --check` catches formatting drift, and pytest
is the only one that actually exercises the code. Run all three.

## Steps

1. **Sync dependencies** if not already done (idempotent):
   ```bash
   cd src/backend && uv sync --extra dev
   ```

2. **Lint:**
   ```bash
   uv run ruff check .
   ```
   The rule set here (`src/backend/pyproject.toml`'s `[tool.ruff.lint]`)
   is deliberately narrow — `E`/`F` (pycodestyle errors + pyflakes),
   `I` (import sorting), `B` (flake8-bugbear correctness footguns like
   mutable default arguments) — correctness and hygiene, not a full
   style regime. An error here is worth fixing for real, not suppressing
   with a bare `# noqa`.

3. **Format check:**
   ```bash
   uv run ruff format --check .
   ```
   If this fails, `uv run ruff format .` applies the fix directly — safe
   to run unconditionally, it only reformats whitespace/quote style, it
   doesn't change behavior.

4. **Test** — needs a real Postgres; see the `test` skill for the
   disposable-container lifecycle if one isn't already reachable:
   ```bash
   PYTHONPATH="$(pwd)/../../" uv run pytest tests -q
   ```
   (or from the repo root: `PYTHONPATH=src uv run --project src/backend pytest src/backend/tests -q`)

5. **Report a consolidated result**: pass/fail for each of the three
   steps, and for any failure, the actual error output. If all three are
   clean, say so plainly.

## If something fails

- **Lint error**: fix the actual issue. An unused import or undefined
  name caught here is exactly the class of thing that's otherwise
  invisible until it causes a runtime `NameError` in a code path the
  test suite doesn't happen to cover.
- **Format check failure**: just run `ruff format .` — there's no
  judgment call here.
- **Test failure**: see the `test` skill and `CLAUDE.md`'s "Critical
  rules" for this codebase's known gotchas (the `backend.*` vs
  `src.backend.*` import path, `bcrypt` pin, ownership-scoping pattern)
  before assuming a failure means the underlying feature is broken
  rather than a test-environment issue.

## Notes

- This mirrors the frontend's own `check` skill (lint → build → test) —
  the backend has no separate "build" step distinct from its tests
  (there's no bundler/compiler to run), so this is lint → format → test
  instead.
- Ruff's rule set was deliberately started narrow (see `pyproject.toml`'s
  comment) rather than enabling every available rule at once — the first
  run on an established codebase with no prior linting would otherwise
  surface a wall of pre-existing style violations unrelated to
  correctness, which drowns out the findings that actually matter. Widen
  it deliberately, a rule category at a time, rather than all at once.

# Backend — AI Learning Platform

FastAPI + SQLAlchemy (async) + PostgreSQL + Alembic backend for an AI-tutoring
platform. Teachers manage courses/classes/tasks; students chat with an LLM
through session-based chat tied to a task. JWT auth via HttpOnly cookie
(Bearer header as fallback for Swagger/API clients).

This file is project memory for whoever (human or Claude) works in this
directory. It leans heavily on lessons from real bugs found and fixed here —
follow the "Rules" sections literally, they exist because violating them
already caused production-shaped bugs once.

## Architecture

```
api/v1/*_routes.py   → HTTP layer: parse request, call a service, map
                        ValueError → 404, PermissionError → 403, else 500
services/*_service.py → business logic + authorization (ownership checks)
repositories/*.py     → thin SQLAlchemy query layer (BaseRepository generic
                        CRUD + per-model custom queries)
models/*.py            → SQLAlchemy ORM models (Base from db/base.py)
schemas/**/*.py        → pydantic request/response validation
agents/, llm/          → the tutoring "brain": agent orchestration + LLM
                          provider abstraction
guardrails/            → content-safety filtering (defense-in-depth only)
```

A request flows: route → `Depends(get_current_user)` / `RoleGuard([...])` →
service method (raises `ValueError`/`PermissionError`, never HTTP concerns)
→ repository/ORM → response schema.

## Critical rules (each exists because breaking it already caused a bug)

**1. Imports are `backend.*`, never `src.backend.*`.**
The package root is `src/backend/` itself — "backend" is the top-level
importable name. Locally this means `PYTHONPATH` must include the repo's
`src/` directory (not the repo root, not `src/backend/`). See "Running
locally" below for the exact invocation — running plain `pytest` or
`python` from inside `src/backend/` will fail with
`ModuleNotFoundError: No module named 'backend'`.

**2. Any query that returns another user's data MUST scope by ownership —
join through to `Course.teacher_id` (or the equivalent chain) and filter
against `current_user.id`.** `RoleGuard([UserRole.TEACHER])` only checks
*role*. It does not check whether the resource belongs to that teacher.
Six analytics endpoints shipped without this once — any teacher could read
any other teacher's student data by ID alone. The correct pattern is
already used throughout `course_service.py`, `class_service.py`,
`task_service.py`, `enrollment_service.py`, and
`session_analytics_service.py`/`prompt_classification_service.py` — copy
that pattern, don't invent a new one.

**3. `_inject_system_prompt` lives once, on `BaseAgent`
(`agents/services/base_agent.py`) — never duplicate it into a subclass.**
It must unconditionally prepend the agent's own system prompt. It used to
have an early-return that skipped injection if the caller's first message
already had `role: "system"`, letting a client fully override the tutor's
persona — and because the logic was copy-pasted per agent subclass instead
of shared, the fix landed in `DirectTutorAgent` but was missed in
`SocraticTutorAgent` for an entire session. If you add a new agent
subclass, it inherits this for free — do not override it.

**4. Every route that isn't intentionally public needs
`Depends(get_current_user)` or `Depends(RoleGuard([...]))`.** Two chat
endpoints (`/chat/direct/stream`, `/chat/direct/generate`) shipped with no
auth dependency at all — anyone could hit them anonymously and run
unlimited LLM calls on the platform's API key.

**5. `bcrypt` is pinned to `4.0.1` in `pyproject.toml` — do not bump it
without testing password hashing end-to-end first.** `passlib==1.7.4`
(unmaintained) has an internal bcrypt self-test that crashes under
`bcrypt>=5.0` (which now hard-rejects >72-byte inputs instead of the old
silent-truncate behavior the self-test probes for). This broke
registration and login *completely* — silently, since it only fails the
first time `hash_password()`/`verify_password()` actually runs, not at
import time. If you ever need a newer bcrypt, verify with:
```python
from backend.auth.security import hash_password, verify_password
h = hash_password("test"); assert verify_password("test", h)
```

**6. `Settings.SECRET_KEY` and `Settings.CORS_ORIGINS` are required, no
usable default.** `SECRET_KEY` must be ≥32 chars (validated in
`core/config.py`) or the app refuses to start — it used to default to
`""`, meaning every JWT would be signed with an empty key if a deployment
forgot to set it. Don't add a default back.

**7. Free-text request fields need `max_length`.** Every `title`/`name`
gets `Field(max_length=255)`, every `description` gets
`Field(max_length=5000)`, chat `content` gets `max_length=8000`. This
bounds both storage and LLM-cost amplification. Follow the existing
schemas as the template for new ones.

**8. `HOST`/`PORT` are runtime-only — no build-time default, no `EXPOSE`
in the Dockerfile.** `entrypoint.sh` uses `${PORT:-8000}` /
`${HOST:-0.0.0.0}` shell fallbacks. Don't add `ENV PORT=...` to the
Dockerfile — that would bake a value in at build time, which is exactly
what was removed on purpose.

**9. A `Settings` field that looks like a toggle must actually be read
somewhere.** This has happened twice: `HOST`/`PORT` existed in `Settings`
while `entrypoint.sh` hardcoded the real values (rule #8), and
`ENABLE_BANLIST_FILTER` existed in `Settings` while
`LLMService._check_banlist` ran unconditionally, never checking it. Both
were invisible to static review and to every test that didn't specifically
assert the toggle's effect. When you add an `ENABLE_*`/config field,
grep for where you expect it to be read and confirm it's actually there
— then write a test that asserts *both* states (on and off) produce
different behavior, not just that the field parses and defaults
correctly. See `tests/unit/test_llm_service.py` for the pattern.

**10. Every route method must catch `ValueError`/`PermissionError` from
its service call and map them to 404/403 — never let them propagate
unhandled.** `task_routes.py` shipped with *no* exception handling at
all on any of its six routes, while `TaskService` raises both
extensively (task not found, wrong owner, not enrolled). Every "not
found" and "access denied" case returned a raw 500 instead of the
correct status — invisible until an integration test asserted the
actual status code for those paths, since a 500 vs. a 404 both "fail
the happy path" identically if you only test success. Every other route
file follows the `try: ... except ValueError as e: raise
HTTPException(404, str(e)) except PermissionError as e: raise
HTTPException(403, str(e))` pattern — copy it exactly for any new route,
and when reviewing an existing one, confirm the wrapper is actually
there rather than assuming it matches its siblings.

## Directory map

| Path | What's there |
|---|---|
| `main.py` | FastAPI app, CORS, lifespan, `/docs` disabled when `ENVIRONMENT=production` |
| `core/config.py` | `Settings` (pydantic-settings) — env loading, validators |
| `api/router.py`, `api/v1/*_routes.py` | Route registration, one file per resource (auth, course, class, task, enrollment, chat, analytics, health) |
| `api/deps.py` | `get_current_user` (cookie → Bearer, blacklist check, decode), `require_teacher`/`require_student`, singleton service factories |
| `utils/role_guard.py` | `RoleGuard([UserRole...])` — role check only, not ownership |
| `auth/security.py` | JWT create/decode (HS256, pinned algorithm), password hash/verify (`bcrypt_sha256` via passlib) |
| `services/` | Business logic: `auth_service`, `course_service`, `class_service`, `task_service`, `enrollment_service`, `session_service`, `conversation_service`, `chat_service`, `chat_history_service`, `session_analytics_service`, `prompt_classification_service`, `context_window_service` |
| `repositories/` | `BaseRepository[T]` generic CRUD + one repo per model with custom queries |
| `models/` | SQLAlchemy models. `postgresql.UUID` primary keys — **tests need real Postgres, SQLite can't run this dialect type** |
| `schemas/` | pydantic I/O schemas, mirrors `models/` roughly |
| `agents/services/` | `BaseAgent`, `DirectTutorAgent` (single-pass), `SocraticTutorAgent` (multi-turn, reflection-driven stage selection), `PromptClassifierAgent` |
| `agents/registry/agent_registry.py` | `AgentRegistry` — `agent_id → (class, yaml config path)`. `direct_tutor` and `socratic_tutor` are both registered; only `direct_tutor` is currently wired to any route |
| `agents/prompts/*.yaml` | Per-agent system prompts and model params, loaded at agent instantiation |
| `llm/` | Provider abstraction (`llm/providers/`, `llm/services/llm_service.py`) — OpenAI, OpenRouter, Gemini, Anthropic, custom, selected via `DEFAULT_LLM_PROVIDER` |
| `guardrails/banlist_filter.py` | Keyword banlist, Unicode-normalized substring match. Explicitly defense-in-depth — not a real moderation guarantee |
| `db/` | `Base` (declarative base), `session.py` (async engine + `get_db`) |
| `alembic/` | Migrations. `alembic.ini`'s `script_location` is relative to itself (`%(here)s/alembic`), so it must stay a sibling of `alembic.ini` |
| `observability/logging/` | `get_logger(__name__)` — use this, not `print` or raw `logging.getLogger` |
| `tests/` | See "Testing" below |

## Running locally

```bash
cd src/backend
uv sync --extra dev

cp ../../.env.be.example ../../.env.be   # from repo root; edit DATABASE_URL to use localhost

# Migrations (from src/backend/, alembic.ini is here)
uv run alembic upgrade head

# Server — must run from src/ (repo_root/src) with PYTHONPATH set, so
# "backend.*" imports resolve (see Critical Rule #1)
cd ..
PYTHONPATH="$(pwd)" uv run --project backend uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Postgres must be running and reachable at whatever `DATABASE_URL` in
`.env.be` says. See the repo root `README.md` for Docker-based setup.

## Testing

```bash
# From the repo root:
PYTHONPATH=src uv run --project src/backend pytest src/backend/tests            # everything
PYTHONPATH=src uv run --project src/backend pytest src/backend/tests/unit       # no DB needed
PYTHONPATH=src uv run --project src/backend pytest src/backend/tests/integration  # needs real Postgres
```

- `tests/unit/` — pure logic, zero DB dependency by design. If a unit test
  needs `db_session`/`client`, it's in the wrong directory.
- `tests/integration/` — real Postgres via `httpx.AsyncClient` against the
  actual FastAPI app. `tests/integration/conftest.py` drops and recreates
  the whole schema before every test (`Base.metadata.drop_all` /
  `create_all`) — don't point it at a database you care about.
- Default test `DATABASE_URL`: `postgresql+asyncpg://test:test@localhost:5433/test`
  (override via env var). A disposable container:
  `docker run -d -p 5433:5432 -e POSTGRES_USER=test -e POSTGRES_PASSWORD=test -e POSTGRES_DB=test postgres:15-alpine`
- When you fix a bug found by a specific exploit/scenario, write the
  regression test for *that scenario*, not just the unit under test in
  isolation — the socratic-agent duplicate bug (Critical Rule #3) would
  have been caught immediately by a test at the concrete-agent level, and
  wasn't for a while because only `DirectTutorAgent` had one.

## Database & migrations

```bash
uv run alembic revision --autogenerate -m "describe your change"
uv run alembic upgrade head
uv run alembic downgrade -1
```

Review every autogenerated migration before committing — autogenerate
does not reliably detect things like column renames (it'll emit a
drop+add) or check constraint changes.

## Docker

- `Dockerfile` builds via `uv sync` (not pip), copies the build context
  (which is `src/backend/` itself) to `/app/backend` inside the image —
  see Critical Rule #1 for why the import path cares about this.
- `entrypoint.sh` runs `alembic -c backend/alembic.ini upgrade head` then
  `exec uvicorn backend.main:app`. No `HEALTHCHECK`-less deploys — the
  Dockerfile's `HEALTHCHECK` hits `/api/v1/health/live`.
- No `EXPOSE`, no build-time `PORT`/`HOST` default — see Critical Rule #8.
- Root `docker-compose.yml` builds locally + runs a local `db` service
  (dev). Root `docker-compose.prod.yml` pulls prebuilt
  `ghcr.io/indonesia-ai-institute/ai-learning-platform-api:${IMAGE_TAG:-latest}`
  images, no local build, no bundled db (external/managed Postgres
  assumed).

## Known, deliberately deferred gaps

Don't "fix" these without a product decision — they were evaluated and
explicitly left as-is:

- **No rate limiting anywhere** (login, register, chat/generate endpoints).
  Needs a library choice (`slowapi` + limits) and real limit values.
- **Registration lets the caller pick `role: teacher` directly** — no
  invite/approval flow exists yet. Any registered "teacher" account can
  create courses and see their own students' analytics (correctly scoped
  per Critical Rule #2), but there's currently no gate on *becoming* a
  teacher in the first place.

## Conventions

- Commit messages follow Angular/conventional-commit style
  (`feat|fix|perf|refactor|docs|style|test|chore|ci|build|revert: ...`) —
  `python-semantic-release` (configured in the repo-root `pyproject.toml`,
  not this project's own) uses this to cut versions and changelogs on
  `main`.
- Logging: `from backend.observability.logging.logger import get_logger`,
  `logger = get_logger(__name__)`. Never leak raw exception text in an
  HTTP response (`logger.exception(...)` + a generic `HTTPException`
  detail) — see `api/v1/analytics_routes.py` for the pattern.
- No comments that just restate the next line. A comment earns its place
  by explaining a non-obvious *why* — a route-ordering constraint, an
  external API quirk, a workaround for a specific bug. Several existing
  comments in this codebase are exactly that (e.g. the `PENTING: route
  static harus SEBELUM route dynamic` warnings in `chat_routes.py`) —
  match that bar, not decorative banners.

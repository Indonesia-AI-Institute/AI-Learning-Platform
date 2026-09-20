# AI Learning Platform — Backend

FastAPI backend for the AI Learning Platform: course/class/task management
for teachers, session-based AI tutoring chat for students, and prompt
analytics that classifies *how* students are using that chat — not just
that they used it. Async SQLAlchemy + PostgreSQL, JWT auth, Alembic
migrations, and a pluggable multi-provider LLM layer (OpenAI, OpenRouter,
Gemini, Anthropic, or any OpenAI-compatible custom endpoint).

The two things worth understanding before touching this codebase, both
covered in detail below: **the agent layer** (`agents/`, `llm/`) that
actually talks to an LLM on a student's behalf, and **the background
classifier** that tags every student message with nine behavior signals in
parallel with the chat response, at zero added latency — see
[Tutoring agents & prompt analytics](#tutoring-agents--prompt-analytics).

For full-stack setup (frontend + backend together, Docker Compose, one-shot
deployment), see the [repo root README](../../README.md). This file covers
working in the backend on its own.

## Tech stack

| Component | Technology |
|---|---|
| Framework | FastAPI |
| Server | Uvicorn (ASGI) |
| ORM | SQLAlchemy 2.0 (async, `asyncpg`) |
| Database | PostgreSQL 15 |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (HS256) via HttpOnly cookie, Bearer header fallback |
| Package manager | [uv](https://docs.astral.sh/uv/) |
| Tests | pytest + pytest-asyncio + httpx |

## Architecture

A request flows through four layers, each with one job:

```
api/v1/*_routes.py    HTTP layer — parse the request, call one service
                       method, map ValueError -> 404 / PermissionError -> 403
       │
       ▼
services/*_service.py  Business logic + authorization (every query that
                       returns another user's data is scoped by ownership —
                       joined through to Course.teacher_id, never role alone)
       │
       ▼
repositories/*.py      Thin SQLAlchemy query layer — BaseRepository[T]
                       generic CRUD + per-model custom queries
       │
       ▼
models/*.py            SQLAlchemy ORM models (postgresql.UUID primary keys)
```

Chat requests take a side path through the tutoring "brain" instead of
straight to the database:

```
chat_routes.py -> conversation_service.py -> agents/ (DirectTutor /
SocraticTutor) -> llm/ (provider abstraction) -> the configured LLM API
```

`guardrails/` sits in front of that path as a defense-in-depth keyword
filter, not a real moderation guarantee. See
[Tutoring agents & prompt analytics](#tutoring-agents--prompt-analytics) for
how the chat response and the background classifier both come out of this
same path without one blocking the other.

## Project layout

```
agents/       agent orchestration (DirectTutor, SocraticTutor, PromptClassifier) + prompt YAML configs
api/          route registration, dependencies (auth/role guards), one *_routes.py per resource
auth/         JWT + password hashing primitives
core/         Settings (env config)
db/           SQLAlchemy engine/session setup
guardrails/   content-safety keyword filter
llm/          LLM provider abstraction (OpenAI/OpenRouter/Gemini/Anthropic/custom)
models/       SQLAlchemy ORM models
observability/ logging setup
repositories/ SQLAlchemy query layer (generic CRUD + per-model queries)
schemas/      pydantic request/response models
services/     business logic + authorization
utils/        role guard, SSE streaming helpers
alembic/      migrations
tests/        pytest suite — unit/ (no DB) and integration/ (real Postgres)
```

See [`CLAUDE.md`](./CLAUDE.md) for the full request-flow architecture, the
established patterns to follow for new code, and a list of hard rules that
exist because breaking them already caused real bugs — worth a read before
making non-trivial changes here.

## Tutoring agents & prompt analytics

This is the part of the backend that's specific to this product, as opposed
to CRUD-over-Postgres plumbing — worth understanding on its own.

**Agents.** `agents/registry/agent_registry.py` maps an `agent_id` to a
`BaseAgent` subclass plus a YAML config (`agents/prompts/*.yaml`) of system
prompts and model params. Two are registered today:

| Agent | Mode | Behavior |
|---|---|---|
| `direct_tutor` (`agents/services/direct_agent.py`) | single-pass | Answers the question directly in one LLM call. **Currently the only agent wired to a live chat route.** |
| `socratic_tutor` (`agents/services/socratic_agent.py`) | multi-turn (up to 3 iterations) | Responds with a guiding question or a hint — never the answer — then runs a reflection pass that scores the student's understanding (LOW/MEDIUM/HIGH) and decides `QUESTION`, `HINT`, or `FINALIZE`. Only once it finalizes does it actually explain. Exists in code and has its own tests, but no route currently routes a real chat session to it. |

Every agent gets its system prompt injected exactly once via
`BaseAgent._inject_system_prompt` — this lives on the base class specifically
so a new subclass can't accidentally skip it (see `CLAUDE.md` Critical Rule
3 for the incident that made this a hard rule).

**The prompt classifier.** `agents/services/prompt_classifier_agent.py`
runs as a *separate* LLM call, entirely decoupled from the chat response.
Every student message gets classified into nine independent boolean
signals (a message can match more than one, all default to `false` if
classification fails):

| Signal | Detects |
|---|---|
| `direct_answer` | Wants the answer outright, no explanation ("Give me the answer") |
| `explanation` | Wants a concept explained ("Why is X?") |
| `step_by_step` | Wants a walkthrough ("How do I solve this?") |
| `example` | Wants an illustration ("Give me an example") |
| `rewrite` | Wants their own work rewritten/improved |
| `feedback` | Wants their attempt checked ("Is this correct?") |
| `summary` | Wants a summary/TL;DR |
| `translation` | Wants something translated |
| `brainstorm` | Wants ideas/options |

These map straight onto the `is_*` boolean columns in
`models/prompt_classification.py` and drive the teacher-facing dashboards
described in the [repo root README](../../README.md#-the-teacher-dashboard).

**Zero added latency, concretely.** `services/conversation_service.py`
never awaits the classifier before returning a response to the student:

- Non-streaming chat (`_classify_and_save` alongside the main reply) uses
  `asyncio.gather(...)` — the LLM reply and the classification call run
  concurrently, and the route only waits on the reply.
- Streaming chat uses `asyncio.create_task(...)` — the classification is
  fired off and forgotten; tokens stream to the client immediately, and the
  classification result is saved whenever it finishes, independent of the
  response stream.

A slow or failed classification call has no effect on how fast a student
sees their answer — it can only ever affect what shows up later on a
teacher's dashboard.

## LLM providers

`DEFAULT_LLM_PROVIDER` selects the provider at startup; `llm/providers/`
implements each one behind a common interface
(`llm/base/llm_providers.py`), so the rest of the codebase never branches on
which one is active.

| Provider | Env var to set | Notes |
|---|---|---|
| `openai` | `OPENAI_API_KEY` | Default `OPENAI_API_BASE` works as-is; override for an Azure/self-hosted OpenAI-compatible gateway |
| `openrouter` | `OPENROUTER_API_KEY` | `OPENROUTER_PROVIDER_ORDER` picks the underlying infra (e.g. `DeepInfra,SiliconFlow`); `OPENROUTER_ALLOW_FALLBACKS`/`OPENROUTER_REQUIRE_PROVIDER` control fallback behavior. Recommended for development — free models available |
| `gemini` | `GEMINI_API_KEY` | Talks to Gemini's OpenAI-compatible endpoint (`GEMINI_API_BASE`) |
| `anthropic` | `ANTHROPIC_API_KEY` | — |
| `custom` | `CUSTOM_LLM_API_KEY`, `CUSTOM_LLM_BASE_URL` | Any OpenAI-compatible endpoint — this is how a self-hosted model (e.g. Ollama at `http://localhost:11434/v1`) plugs in |

`DEFAULT_LLM_MODEL`, `DEFAULT_TEMPERATURE`, `DEFAULT_MAX_TOKENS`, and
`DEFAULT_TIMEOUT` apply regardless of which provider is selected.

## Getting started

**Prerequisites:** Python 3.11+, [uv](https://docs.astral.sh/uv/), a
reachable PostgreSQL 15 instance.

```bash
# From src/backend/
uv sync --extra dev

# Configure environment (from the repo root)
cd ../..
cp .env.be.example .env.be
# edit .env.be — set DATABASE_URL to point at your Postgres (use
# "localhost", not "db", when running outside Docker)

cd src/backend
uv run alembic upgrade head
```

**Run the server.** Imports use the `backend.*` package path, which
requires `src/` (not the repo root, not `src/backend/`) on `PYTHONPATH`:

```bash
# From the repo root:
PYTHONPATH=src uv run --project src/backend uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API is now at `http://localhost:8000`, interactive docs at
`http://localhost:8000/docs` (disabled automatically when
`ENVIRONMENT=production`).

**Or run it via Docker** instead of installing anything locally — see the
[repo root README](../../README.md#-quick-start).

## Environment variables

Copy `.env.be.example` (at the repo root) to `.env.be` and fill in the
values. All settings are defined in [`core/config.py`](./core/config.py)
(pydantic-settings, `case_sensitive=True`); this is the authoritative list.

| Variable | Default | Notes |
|---|---|---|
| `APP_NAME` | `AI Learning Platform Backend` | Cosmetic |
| `APP_VERSION` | `1.0.0` | Cosmetic |
| `ENVIRONMENT` | `development` | Set to `production` to disable `/docs` and `/redoc` |
| `DEBUG` | `false` | — |
| `HOST` | `0.0.0.0` | Only meaningful running outside Docker — see "Docker" below |
| `PORT` | `8000` | Same caveat |
| `SECRET_KEY` | — (**required**) | ≥32 chars, signs every JWT. No usable default — the app refuses to start rather than silently sign tokens with an empty key |
| `DATABASE_URL` | — (**required**) | `postgresql+asyncpg://...`. Use `localhost` outside Docker, `db` (the compose service name) inside it |
| `CORS_ORIGINS` | — (**required**) | JSON array, e.g. `["http://localhost:3000"]`. No wildcard default on purpose — an unset value must fail closed, not open |
| `COOKIE_DOMAIN` | `None` | Domain of the `access_token` cookie. Set to the shared parent (e.g. `.example.com`) when the frontend and API are on different subdomains — otherwise the cookie is host-only to the API and the frontend's route guard never sees it. Leave empty for local/same-host setups |
| `DEFAULT_LLM_PROVIDER` | `openai` | `openai` \| `openrouter` \| `gemini` \| `anthropic` \| `custom` — see [LLM providers](#llm-providers) |
| `DEFAULT_LLM_MODEL` | `gpt-4o` | Model id for the selected provider |
| `DEFAULT_TEMPERATURE` | `0.7` | — |
| `DEFAULT_MAX_TOKENS` | `2048` | — |
| `DEFAULT_TIMEOUT` | `60` | Seconds |
| `OPENAI_API_KEY` / `OPENAI_API_BASE` | `None` / `https://api.openai.com/v1` | Required if `DEFAULT_LLM_PROVIDER=openai` |
| `OPENROUTER_API_KEY` / `OPENROUTER_API_BASE` | `None` / `https://openrouter.ai/api/v1` | Required if using OpenRouter |
| `OPENROUTER_PROVIDER_ORDER` | `None` | Comma-separated, e.g. `DeepInfra,SiliconFlow`. Empty = auto-select |
| `OPENROUTER_ALLOW_FALLBACKS` | `true` | Fall back to another provider if the preferred one is unavailable |
| `OPENROUTER_REQUIRE_PROVIDER` | `false` | Only use `OPENROUTER_PROVIDER_ORDER`, no fallback |
| `GEMINI_API_KEY` / `GEMINI_API_BASE` | `None` / Gemini's OpenAI-compatible endpoint | Required if using Gemini |
| `ANTHROPIC_API_KEY` | `None` | Required if using Anthropic |
| `CUSTOM_LLM_API_KEY` / `CUSTOM_LLM_BASE_URL` | `None` / `None` | Required if `DEFAULT_LLM_PROVIDER=custom` |
| `STREAM_TIMEOUT_SECONDS` | `60` | — |
| `STREAM_KEEP_ALIVE` | `true` | — |
| `ENABLE_STREAMING` | `true` | — |
| `ENABLE_RAG` | `false` | Reserved — not implemented yet |
| `ENABLE_WEBSEARCH` | `false` | Reserved — not implemented yet |
| `LOG_LEVEL` | `INFO` | — |
| `LOG_FILE` | `logs/app.log` | Read directly via `os.getenv` in `observability/logging/`, not through `Settings` |
| `ENABLE_BANLIST_FILTER` | `true` | Toggles the `guardrails/banlist_filter.py` keyword check |
| `BANNED_KEYWORDS` | `["illegal", "exploit", "bypass"]` | Only takes effect if the toggle above is `true` |

Two things worth knowing that aren't in the table because they're **not**
environment-configurable, despite looking like they might be:
- Access tokens expire after a hardcoded 60 minutes
  (`ACCESS_TOKEN_EXPIRE_MINUTES` in `auth/security.py`) — there's no env
  var for this.
- `find_project_root()` in `core/config.py` walks up from this file
  looking for a `.git` directory to locate the repo root, then loads
  `.env.be` (or `.env`) from there. Running the backend from somewhere
  that isn't inside this git repo (e.g. a copied-out `src/backend/` with
  no `.git` anywhere above it) means env vars must be set some other way
  — a `.env` file won't be auto-discovered.

## Testing

```bash
# From the repo root — unit tests need no database at all:
PYTHONPATH=src uv run --project src/backend pytest src/backend/tests/unit

# Integration tests need a real Postgres (models use
# sqlalchemy.dialects.postgresql.UUID, which SQLite can't run). Point
# DATABASE_URL at any disposable instance — each test run drops and
# recreates the schema, so don't use one you care about:
docker run -d -p 5433:5432 -e POSTGRES_USER=test -e POSTGRES_PASSWORD=test -e POSTGRES_DB=test postgres:15-alpine
PYTHONPATH=src uv run --project src/backend pytest src/backend/tests/integration

# Everything:
PYTHONPATH=src uv run --project src/backend pytest src/backend/tests
```

`/test` (this project's Claude Code skill, under `.claude/skills/test/`)
automates the container lifecycle above if you're driving this through
Claude Code.

## Database migrations

```bash
uv run alembic revision --autogenerate -m "describe your change"
uv run alembic upgrade head
uv run alembic downgrade -1
```

Always review an autogenerated migration before applying it —
autogenerate doesn't reliably detect renames or constraint-only changes.

## API overview

All routes are prefixed `/api/v1`. Full interactive reference (request/
response schemas, try-it-out) at `/docs` in non-production environments —
the table below is for quickly finding the right route without opening it.

**Auth** (`api/v1/auth_routes.py`)

| Method & path | Does |
|---|---|
| `POST /auth/register` | Create an account — `role: "student"` or `"teacher"`, self-selected with no invite/approval gate (see `CLAUDE.md`'s "Known, deliberately deferred gaps") |
| `POST /auth/login` | Sets the `access_token` HttpOnly cookie (scoped by `COOKIE_DOMAIN`, `Secure` when `ENVIRONMENT=production`) |
| `POST /auth/logout` | Blacklists the current token |
| `GET /auth/me` | Current user, from the cookie/Bearer token |

**Courses** (`api/v1/course_routes.py`)

| Method & path | Does |
|---|---|
| `POST /courses/create/` | Teacher-only. Create a course |
| `GET /courses/all` | Every active course, any authenticated user (e.g. students browsing what's available) |
| `GET /courses/` | Just the current user's own courses (taught, or enrolled-in depending on role) |
| `GET /courses/{course_id}` | Detail, ownership/enrollment-checked |
| `PUT /courses/{course_id}` | Teacher-only, owner-only |
| `DELETE /courses/{course_id}` | Teacher-only, owner-only |

**Classes** (`api/v1/class_routes.py`)

| Method & path | Does |
|---|---|
| `POST /classes/` | Create a class under a course |
| `GET /classes/course/{course_id}` | Classes in one course |
| `GET /classes/` | Current user's own classes |
| `GET /classes/{class_id}` | Detail |
| `PUT /classes/{class_id}` | Update |
| `DELETE /classes/{class_id}` | Delete |

**Tasks** (`api/v1/task_routes.py`)

| Method & path | Does |
|---|---|
| `POST /tasks/course/{course_id}` | Create a task under a course |
| `GET /tasks/course/{course_id}` | Tasks in one course |
| `GET /tasks/class/{class_id}` | Tasks visible to one class |
| `GET /tasks/{task_id}` | Detail |
| `PUT /tasks/{task_id}` | Update |
| `DELETE /tasks/{task_id}` | Delete |

**Enrollments** (`api/v1/enrollment_routes.py`)

| Method & path | Does |
|---|---|
| `POST /enrollments/` | Student joins a class |
| `DELETE /enrollments/{enrollment_id}` | Leave a class |
| `GET /enrollments/me` | Current student's enrollments |
| `GET /enrollments/class/{class_id}` | Teacher: roster for one class |

**Chat** (`api/v1/chat_routes.py`) — see [Tutoring agents & prompt analytics](#tutoring-agents--prompt-analytics)

| Method & path | Does |
|---|---|
| `POST /chat/direct/stream`, `POST /chat/direct/generate` | One-off chat, not tied to a session/task |
| `POST /chat/sessions/task/{task_id}` | Start a session scoped to a task |
| `GET /chat/sessions/my` | Current student's sessions |
| `GET /chat/sessions/task/{task_id}` | Sessions for one task |
| `GET /chat/sessions/{session_id}` | Session detail |
| `POST /chat/sessions/{session_id}/stream` | Send a message, stream the reply (SSE) — this is where classification fires in the background |
| `POST /chat/sessions/{session_id}/end` | Explicitly end a session |
| `POST /chat/sessions/{session_id}/resume` | Resume an ended session |
| `POST /chat/sessions/{session_id}/auto-end` | Called by the frontend on unmount/navigate-away |
| `DELETE /chat/sessions/{session_id}` | Delete a session |
| `GET /chat/sessions/{session_id}/history` | Full message history |
| `GET /chat/teacher/student/{student_id}/sessions` | Teacher: a student's sessions across the teacher's own courses |
| `GET /chat/teacher/sessions/{session_id}/history` | Teacher: full history of any session in a course they teach |

**Analytics** (`api/v1/analytics_routes.py`) — every route here is
ownership-scoped, never role-only (see `CLAUDE.md` Critical Rule 2)

| Method & path | Does |
|---|---|
| `GET /analytics/me` | Student: own summary |
| `GET /analytics/me/classifications` | Student: own 9-signal breakdown |
| `GET /analytics/class/{class_id}` | Teacher: class summary |
| `GET /analytics/class/{class_id}/classifications` | Teacher: class's 9-signal breakdown |
| `GET /analytics/course/{course_id}/classifications` | Teacher: course-wide breakdown |
| `GET /analytics/task/{task_id}` | Teacher: task summary |
| `GET /analytics/task/{task_id}/classifications` | Teacher: task's 9-signal breakdown |
| `GET /analytics/student/{student_id}/classifications` | Teacher: one student's breakdown |
| `GET /analytics/sessions/{session_id}` | Teacher: one session's analytics |

**Health** (`api/v1/health_routes.py`)

| Method & path | Does |
|---|---|
| `GET /health` | Basic check |
| `GET /health/ready` | Readiness (DB reachable) |
| `GET /health/live` | Liveness — what the Docker `HEALTHCHECK` hits |

## Docker

```bash
docker build -t ailearning-api -f Dockerfile .
```

- Builds via `uv sync` (not pip); the build context (`src/backend/` itself)
  is copied to `/app/backend` inside the image — the import path cares
  about this exact layout (see `CLAUDE.md` Critical Rule 1).
- `entrypoint.sh` runs `alembic -c backend/alembic.ini upgrade head`, then
  `exec uvicorn backend.main:app` — migrations happen automatically on
  every container start.
- No `EXPOSE`, no build-time `PORT`/`HOST` default — both are
  runtime-only, read via `${PORT:-8000}`/`${HOST:-0.0.0.0}` shell
  fallbacks in `entrypoint.sh`.
- `HEALTHCHECK` hits `/api/v1/health/live`.
- Root `docker-compose.yml` builds this image locally and runs a bundled
  `db` service (dev). Root `docker-compose.prod.yml` pulls the prebuilt
  `ghcr.io/indonesia-ai-institute/ai-learning-platform-api:${IMAGE_TAG:-latest}`
  image and assumes an external/managed Postgres — no bundled `db`, and
  the API isn't given a host port mapping (not exposed to the internet
  directly in production).

## Troubleshooting

**`ModuleNotFoundError: No module named 'backend'`** — you ran `pytest` or
`uvicorn` from inside `src/backend/`, or without `PYTHONPATH` set. The
importable package root is `src/`, not `src/backend/` and not the repo
root. Run from the repo root with `PYTHONPATH=src` (see "Getting started"
and "Testing" above) — this is the single most common way to hit this.

**App refuses to start with a `SECRET_KEY` validation error** — it must be
≥32 random characters; there's no usable default on purpose (see
`CLAUDE.md` Critical Rule 6). Generate one with
`python -c "import secrets; print(secrets.token_urlsafe(32))"`.

**Login/registration fails, or `verify_password` raises** — check that
`bcrypt` is still pinned to `4.0.1` in `pyproject.toml`. `passlib==1.7.4`
(the hashing library this project uses) has an internal self-test that
crashes under `bcrypt>=5.0`. If you need a newer bcrypt, verify hashing
end-to-end first — see `CLAUDE.md` Critical Rule 5.

**Login returns 200 but the user lands back on `/login`** — the frontend
and API are on different subdomains and `COOKIE_DOMAIN` isn't set, so the
`access_token` cookie is host-only to the API and the frontend's route
guard never sees it. Set `COOKIE_DOMAIN` to the shared parent (e.g.
`.example.com`), serve both over HTTPS with `ENVIRONMENT=production`, and
log in again.

**Integration tests fail with a dialect/UUID-related error on SQLite** —
they're not supposed to run on SQLite at all. Models use
`sqlalchemy.dialects.postgresql.UUID`; integration tests need a real
Postgres (see "Testing" above).

**A new `ENABLE_*`/config toggle doesn't seem to do anything** — confirm
it's actually read somewhere, not just defined in `Settings`. This has
shipped broken twice (see `CLAUDE.md` Critical Rule 9) — grep for where
you expect the toggle to be checked, and write a test asserting both
states produce different behavior.

## Claude Code project tooling

This directory has its own `.claude/`:

- **`CLAUDE.md`** — architecture, hard conventions, and known gaps.
- **`.claude/skills/`** — thirteen skills, each invocable as `/<name>` or
  picked up automatically when relevant:
  - **`dev-server`** — start the backend locally the correct way (env,
    migrations, `PYTHONPATH`, reload).
  - **`check`** — comprehensive check: ruff lint + format check, then the
    pytest suite, with one consolidated report.
  - **`test`** — run the pytest suite, handling the Postgres test
    container lifecycle.
  - **`docker-smoke-test`** — build the Docker image and exercise it end
    to end (migrations, auth flow, health check) against a real Postgres
    container.
  - **`new-endpoint`** — scaffold a new route + service + schema
    following this codebase's conventions.
  - **`new-model`** — scaffold a brand-new table (model + repository +
    registering it for Alembic), the step before `new-endpoint`.
  - **`new-agent`** — scaffold a new tutoring agent (prompt config,
    `BaseAgent` subclass, registry entry, tests) — with the
    system-prompt-injection rule (Critical Rule #3) baked into the steps.
  - **`new-guardrail`** — scaffold a new content-safety filter (filter
    class, config toggle, `LLMService` wiring, tests) — with the
    "toggles must actually be read" rule (Critical Rule #9) baked in.
  - **`new-config-var`** — add a new `Settings`/env var correctly,
    including confirming it's actually read where intended — the exact
    class of bug behind Critical Rule #9, which has shipped twice.
  - **`enrich-unit-tests`** — audit and deepen `tests/unit/` coverage:
    untested pure logic, boundary/negative cases, duplicated-logic risk.
  - **`enrich-integration-tests`** — audit and deepen
    `tests/integration/` coverage: the full response-code matrix per
    route, and the two-independent-tenants IDOR fixture pattern.
  - **`db-migrate`** — generate and sanity-check an Alembic migration.
  - **`security-check`** — review a diff against this backend's specific
    security checklist (ownership scoping, auth gates, prompt-injection
    surface, etc.).

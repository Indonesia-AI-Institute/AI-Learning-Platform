---
name: enrich-integration-tests
description: Audit and deepen integration test coverage in tests/integration/ — find routes without real-HTTP/real-Postgres coverage, add auth/ownership/IDOR/validation tests against realistic multi-tenant data, and verify new tests actually catch regressions. Use when asked to improve, expand, enrich, or add more detail to the backend's integration tests, or to audit endpoint coverage for auth/authorization gaps.
---

# Enrich integration tests

Deepen `tests/integration/` coverage for whatever scope was described in
this invocation (a specific route/resource, or a general audit if none
was given).

Read `src/backend/CLAUDE.md` first if you haven't already this session.
The analytics IDOR bug (Critical Rule #2 — six endpoints checked role but
not ownership) was found by security review, but it's exactly the kind of
thing `tests/integration/test_analytics_idor.py` now exists specifically
to keep caught: real HTTP requests, real cross-tenant data, real
assertions that teacher A gets nothing back for teacher B's resources.
That file is the template for this whole skill.

## What belongs in `tests/integration/`

Anything that needs the real FastAPI app wired to a real database:
end-to-end request handling, ownership scoping that only shows up as a
SQL join, auth state that spans requests (login → use token → logout →
reuse token). Uses `httpx.AsyncClient` against the actual ASGI app (the
`client` fixture in `tests/conftest.py`), not mocked services — if a test
mocks out the service/repository layer instead of hitting a real
database, it's not actually integration-testing anything and probably
belongs in `tests/unit/` as a mocked-orchestration test instead (see
`enrich-unit-tests`'s guidance on that).

Every test gets a **fresh, empty schema** (`tests/integration/conftest.py`
drops and recreates everything, autouse, before each test) — never
assume seed data exists; every fixture builds exactly the rows a test
needs, and nothing more.

## Steps

1. **Pick the target.** If given a specific resource/route, scope to
   that. Otherwise, survey `api/v1/*_routes.py` against
   `tests/integration/` and find routes with no corresponding test file
   or clearly thin coverage — `chat_routes.py` (beyond the direct/*
   auth-gate tests already there), `course_routes.py`, `class_routes.py`,
   `task_routes.py`, and `enrollment_routes.py` are plausible gaps as of
   this writing; verify against what actually exists before assuming.

2. **For every route in scope, cover the full response-code matrix that
   actually applies to it:**
   - **200/201 happy path** with realistic data.
   - **401** with no auth token, if the route requires auth (it almost
     always should — see Critical Rule #4).
   - **403** with the wrong role (a student hitting a teacher-only route
     or vice versa), if role-restricted.
   - **404** for a resource ID that doesn't exist.
   - **403 or an empty/filtered result** — not another user's data — for
     a resource ID that exists but belongs to someone else. This is the
     ownership/IDOR check, and it's the single most valuable thing this
     skill adds. See "The IDOR fixture pattern" below.
   - **422** for a request body that violates schema validation (missing
     required field, a `max_length` violation) — confirms the schema
     constraint is actually wired to the route, not just defined.

3. **The IDOR fixture pattern** (copy `tests/integration/test_analytics_idor.py`'s
   shape): build **two fully independent data graphs** — teacher A with
   their own course/class/task/student/session, teacher B with their
   own, via direct ORM inserts through `db_session` (not the API — faster,
   and decouples the fixture from the endpoints under test). Then assert
   teacher A's token against teacher B's resource IDs gets a 403 or an
   empty result, never B's actual data. Do this for every endpoint that
   takes a resource ID and returns data scoped to "the current teacher's
   own X" — that's the exact shape the original six-endpoint IDOR bug had.

4. **For auth-flow-adjacent changes**, mirror
   `tests/integration/test_auth_flow.py`'s style: real register/login
   through the HTTP layer (not calling the service directly), and for
   anything token-lifecycle-related, prove the *end state* over multiple
   requests — e.g. "logout then reuse the same token" is a two-request
   test, not a single assertion.

5. **Build fixtures with `db_session` directly**, not by chaining HTTP
   calls to set up state, when the setup itself isn't what's under test —
   faster, and it isolates "does this endpoint work" from "does the
   *setup* endpoint work." Reserve HTTP-call chains for tests where the
   sequence of requests is itself the behavior being verified (auth flow,
   session lifecycle).

6. **Prove new tests actually have teeth before calling this done.**
   Pick at least one new test per route, temporarily revert the
   authorization/validation check it covers, confirm the test fails, then
   restore it and confirm it passes again. This is how the original IDOR
   fix was verified — reverting `get_class_analytics`'s teacher_id filter
   made exactly one test fail, confirming the suite would actually catch
   a regression, not just exercise the code path.

7. **Run via the `test` skill** (handles the disposable Postgres
   container lifecycle) — confirm the full suite passes, then confirm it
   still passes on a second run (schema reset must be clean and
   idempotent, not order-dependent on leftover state from a prior run).

## Before finishing

Report what was added per route (happy path / 401 / 403 / IDOR / 422 —
which of these existed before vs. are new), and call out any route where
you *couldn't* write the IDOR check because the ownership model itself is
unclear or the route doesn't take a resource ID at all — that's worth
surfacing, not silently skipping.

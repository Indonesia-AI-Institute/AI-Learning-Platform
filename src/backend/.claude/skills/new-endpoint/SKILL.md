---
name: new-endpoint
description: Scaffold a new backend API endpoint (schema + service method + route) following this codebase's established conventions — request-flow layering, ownership scoping, auth dependencies, and test coverage. Use when asked to add a new backend route or REST endpoint.
---

# New backend endpoint

Scaffold a new endpoint for whatever resource/behavior was described in
this invocation.

Read `src/backend/CLAUDE.md` first if you haven't already this session —
it documents the request-flow architecture, and the hard rules below
exist because violating them already caused real bugs.

## What to build, in order

1. **Schema(s)** in `src/backend/schemas/<resource>/` — request schema(s)
   with `Field(...)` constraints on every free-text field
   (`max_length=255` for titles/names, `max_length=5000` for
   descriptions, or whatever's appropriate for the specific field — look
   at sibling schemas in the same directory for the established pattern
   before inventing new limits). A response schema only if the existing
   ORM-object-as-response pattern (see other routes returning models
   directly) doesn't fit.

2. **Service method** in `src/backend/services/<resource>_service.py` (or
   a new file if this is a genuinely new resource, matching the
   `<resource>_service.py` naming convention). Business logic and
   **authorization** live here, not in the route:
   - Raise `ValueError` for "not found" — routes map this to 404.
   - Raise `PermissionError` for "not allowed" — routes map this to 403.
   - **If this endpoint returns or modifies another user's data**, it
     MUST scope the query by ownership — join through to
     `Course.teacher_id` (or whatever the correct ownership chain is for
     this resource) and filter against `current_user.id`. Do not rely on
     a role check alone (`RoleGuard([UserRole.TEACHER])` checks role,
     not ownership — six endpoints shipped without ownership scoping
     once; don't repeat it). Look at `course_service.py`,
     `class_service.py`, or `task_service.py` for the exact pattern to
     copy.

3. **Repository method** in `src/backend/repositories/<resource>_repository.py`
   only if `BaseRepository`'s generic `create`/`get`/`get_all`/`update`/
   `delete`/`filter_by` don't cover the query — most ownership-scoped
   joins belong directly in the service method (that's the existing
   pattern for `session_analytics_service.py`/
   `prompt_classification_service.py`), not pushed down into a generic
   repository.

4. **Route** in `src/backend/api/v1/<resource>_routes.py`:
   - Auth dependency: `Depends(get_current_user)` for any authenticated
     user, `Depends(RoleGuard([UserRole.TEACHER]))` /
     `Depends(RoleGuard([UserRole.STUDENT]))` for role-restricted. A
     route with **no** auth dependency at all must be deliberate and
     rare (health checks, public read endpoints) — confirm with the user
     if it's not obviously one of those; two chat endpoints once shipped
     with no auth dependency by omission, not by design.
   - Wrap the service call: `except ValueError as e: raise
     HTTPException(404, str(e))`, `except PermissionError as e: raise
     HTTPException(403, str(e))`.
   - For any other exception the service might raise, log it
     server-side (`logger.exception(...)`) and return a **generic**
     `HTTPException(500, "...")` message — never `str(e)` in the
     response detail; that can leak SQL/internal details to the client.
   - If this route's path could conflict with a dynamic sibling route
     (e.g. a static `/my` alongside a dynamic `/{id}`), register the
     static one first and leave a comment saying why — see
     `chat_routes.py` for existing examples of this exact gotcha.
   - Register the router in `src/backend/api/router.py` if this is a new
     resource file.

5. **Tests** — at minimum:
   - `tests/unit/` — schema validation (accepts valid input, rejects
     over-limit/malformed input).
   - `tests/integration/` — the endpoint through the real HTTP layer:
     happy path, auth-required (401 with no token), and — if this
     endpoint touches another user's data — an IDOR test proving a
     second user can't reach the first user's data through it. See
     `tests/integration/test_analytics_idor.py` for the two-independent-
     teachers pattern to copy.

## Before finishing

- Use the `test` skill (or just run the relevant new test files) to
  confirm everything passes.
- If you're unsure whether this endpoint needs ownership scoping, ask —
  don't guess either way on an authorization decision.

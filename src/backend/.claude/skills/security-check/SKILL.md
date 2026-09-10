---
name: security-check
description: Review backend changes against this codebase's specific security checklist, built from real vulnerabilities found and fixed here — ownership scoping, auth gates, agent prompt-injection surface, exception leakage, and more. Not a generic OWASP pass. Use when asked to security-review backend changes, or before merging/deploying anything touching auth, permissions, or agent prompt handling.
---

# Backend security check

Review target: whatever diff/branch/area was described in this
invocation (default to the current diff/branch if nothing more specific
was given).

This is a targeted checklist from findings actually made in this
codebase, not a generic scan — every item below is here because it was a
real bug once, not a theoretical concern. Read the relevant source before
answering each question; don't infer from naming alone.

## Checklist

**1. Ownership, not just role.** For every route/query touched that
returns or modifies data scoped to a specific teacher/student/course: does
it filter by `Course.teacher_id == current_user.id` (or the equivalent
ownership chain for the resource), or only by `RoleGuard`/role? A role
check alone lets any teacher read any other teacher's data. Grep for new
`RoleGuard([UserRole.TEACHER])` usages and check what the service method
behind them actually filters by.

**2. Auth dependency on every non-public route.** Does every new/changed
route have `Depends(get_current_user)` or `Depends(RoleGuard([...]))`
somewhere in its dependency chain? A route with none at all must be
deliberately public (health checks, etc.) — flag anything else.

**3. Agent system prompt integrity.** If anything touches
`agents/services/*.py` or how `messages` get built before reaching an
agent: can a caller-supplied message with `role: "system"` end up
anywhere in `messages` before it reaches `_inject_system_prompt`? Confirm
`_inject_system_prompt` (on `BaseAgent`, `agents/services/base_agent.py`)
is being used as-is and hasn't been re-implemented per-subclass again —
that exact duplication is how this broke once already.

**4. Free-text field length limits.** Any new pydantic schema field
holding user-supplied text (`title`, `name`, `description`, chat
`content`, `system_prompt`, etc.) — does it have `Field(max_length=...)`?
Missing limits compound LLM-cost amplification and unbounded storage.

**5. No raw exception leakage.** Any `except Exception as e: raise
HTTPException(..., detail=str(e))` (or equivalent) in changed route code?
That can leak SQL fragments, internal paths, or stack details to the
client. Should be `logger.exception(...)` + a generic detail message.

**6. Secrets and config.** Any new required-at-runtime secret/config
value — does it have real validation (non-empty, sane length/format) at
`Settings` construction time, or could the app boot successfully with a
silently-broken value? (`SECRET_KEY`/`CORS_ORIGINS` are the existing
examples of "required, validated, no usable default.")

**7. Auth/password primitive changes.** Any change to
`auth/security.py`, or a dependency bump touching `passlib`, `bcrypt`, or
`python-jose` in `pyproject.toml`? If so, this needs the
`docker-smoke-test` skill run against it, not just unit tests — the
`bcrypt`/`passlib` incompatibility that broke login entirely was invisible
to everything except an actual live password hash/verify call.

**8. Rate limiting / abuse surface.** Does a new endpoint call an LLM
provider or do anything else with real per-request cost? There's
currently no rate limiting anywhere in this app (a known, deliberately
deferred gap — see `CLAUDE.md`) — don't treat "no rate limiting on this
new endpoint either" as a new finding, but do flag if the new endpoint is
unusually expensive per call (e.g. no result-size cap) even by that
already-accepted baseline.

**9. Every route actually catches `ValueError`/`PermissionError` from
its service call.** `task_routes.py` shipped with none of its six routes
doing this, so every "not found" and "access denied" case returned a raw
500 instead of 404/403 — invisible to a review that only checks the
happy path. Confirm any new/changed route follows the `except ValueError
as e: raise HTTPException(404, ...) except PermissionError as e: raise
HTTPException(403, ...)` pattern used everywhere else, rather than
assuming it matches its siblings just because the file looks similar.

## Output

Report findings the same way the project's `code-review`/security-review
conventions do: severity (Critical/High/Medium/Low), file:line, a
concrete scenario (not just "this could be a problem"), and a suggested
fix. If a checklist item doesn't apply to the change under review, say so
briefly rather than omitting it — that's a "checked, fine" note, not
padding.

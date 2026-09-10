---
name: enrich-unit-tests
description: Audit and deepen unit test coverage in tests/unit/ — find untested pure logic, add boundary/negative/edge-case tests, and verify new tests actually catch regressions. Use when asked to improve, expand, enrich, or add more detail to the backend's unit tests, or to audit unit test coverage for a specific module.
---

# Enrich unit tests

Deepen `tests/unit/` coverage for whatever scope was described in this
invocation (a specific file/module, or a general audit if none was
given).

Read `src/backend/CLAUDE.md` first if you haven't already this session.
The most valuable unit test written in this codebase so far wasn't found
by looking for bugs — it was found by writing a thorough test for
`SocraticTutorAgent`, which had zero coverage, and discovering its
`_inject_system_prompt` was an unfixed duplicate of a CRITICAL
vulnerability already fixed in `DirectTutorAgent`. Treat "no tests exist
for this" as a signal worth investigating on its own, not just a coverage
gap to fill mechanically.

## What belongs in `tests/unit/`

Pure logic with **no** database dependency — if a test needs `db_session`
or `client`, it belongs in `tests/integration/` instead, not here. This
boundary is enforced by fixture placement (`tests/integration/conftest.py`
holds the only autouse schema-reset fixture; the root `tests/conftest.py`
declares `engine`/`db_session`/`client` but never invokes them
automatically) — a correctly-scoped unit test never touches a real
database, provably: `DATABASE_URL=postgresql+asyncpg://nope:nope@127.0.0.1:1/nope
uv run pytest tests/unit` should still pass 100%. Run that as a sanity
check after adding tests, not just the normal suite.

## Steps

1. **Pick the target.** If given a specific file/module, scope to that.
   Otherwise, survey `src/backend/` for pure-logic modules with thin or
   absent `tests/unit/` coverage: `grep -rL` the test directory against
   modules in `auth/`, `guardrails/`, `agents/services/`, `utils/`,
   `schemas/`, `core/`, and any `services/*.py` methods that don't touch
   `self.db` at all (rare, but check).

2. **Read the actual implementation before writing tests against your
   assumption of what it does.** This caught real bugs before: the JWT
   expiry test initially assumed `exp - iat` was a `timedelta` (wrong —
   they're numeric epoch-second claims once round-tripped through
   encode/decode), and the alg=none JWT test initially tried to construct
   the forged token via `jose.jwt.encode(..., algorithm="none")`, which
   `python-jose` itself refuses to create — the token had to be
   hand-built from base64 segments instead.

3. **For each function/method in scope, cover:**
   - The obvious happy path (already likely covered — don't stop here).
   - **Boundaries, exactly at the edge**: if there's a `max_length=255`,
     test 255 (accepted) *and* 256 (rejected) — not just "way over the
     limit." Off-by-one is the most common way a limit is silently
     wrong. See `tests/unit/test_schema_limits.py` for the pattern.
   - **Negative/malformed input**: empty string, `None` where optional,
     wrong type, garbage/unparseable input, duplicate entries, whitespace-
     only strings.
   - **Security-relevant inputs specifically**, if the module touches
     auth/tokens/guardrails/prompt-assembly: forged signatures, expired
     tokens, algorithm-confusion attempts, caller-controlled content that
     could smuggle a role/instruction override, Unicode/spacing evasion
     of a filter. See `tests/unit/test_auth_security.py` and
     `tests/unit/test_base_agent.py` for the depth expected here.
   - **State/mutation behavior**: does the function mutate its input
     (it usually shouldn't)? Is a returned collection a defensive copy
     or a live reference (`tests/unit/test_banlist_filter.py::test_get_all_keywords_returns_copy`
     is the template)?

4. **Look for duplicated logic while you're in there.** If two classes
   have near-identical private methods (the way `DirectTutorAgent` and
   `SocraticTutorAgent` once both defined `_inject_system_prompt`
   independently), that's a standing risk that a fix lands in one copy
   and not the other. Flag it — and if it's safe and in scope, refactor
   the shared logic onto a common base the way `BaseAgent` now owns
   `_inject_system_prompt`, then test the shared implementation directly
   *plus* a defense-in-depth regression test at each concrete call site
   (see `test_base_agent.py` + `test_direct_agent.py` +
   `test_socratic_agent.py` for that three-layer pattern).

5. **Mock external calls, don't hit them.** LLM provider calls
   (`llm_service.generate`/`stream_generate`) get mocked with
   `unittest.mock.AsyncMock` — see `tests/unit/test_socratic_agent.py`'s
   `_mock_llm` helper for the sequential-response pattern used to test
   multi-stage orchestration (reflection call → branch call).

6. **Prove new tests actually have teeth before calling this done.**
   Pick at least one new test per file, temporarily break the
   implementation it covers (comment out a check, revert a fix), confirm
   the test fails, then restore the implementation and confirm it passes
   again. A test that can't fail isn't testing anything — this exact
   technique caught that an early IDOR test would have passed even with
   the vulnerability still present, before the ownership filter was
   verified this way.

7. **Run the full unit suite** (via the `test` skill, or directly) with
   an unreachable `DATABASE_URL` to confirm nothing accidentally pulled
   in a database dependency, then with a real one for completeness.

## Before finishing

Report what was added (file, count, what kind of gap each group closes —
"boundary", "negative input", "previously zero coverage", "regression for
bug X"), and separately call out anything found along the way that looks
like a real bug rather than a test gap — don't silently fix unrelated
bugs without saying so, the way the `ENABLE_BANLIST_FILTER` dead-toggle
and the `SocraticTutorAgent` duplicate were both found this way and
called out explicitly before fixing.

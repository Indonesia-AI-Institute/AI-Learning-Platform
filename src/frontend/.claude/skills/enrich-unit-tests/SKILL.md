---
name: enrich-unit-tests
description: Audit and deepen unit test coverage in tests/unit/ — find untested pure logic and hooks, add boundary/negative/edge-case tests, and verify new tests actually catch regressions via mutation testing. Use when asked to improve, expand, enrich, or add more detail to the frontend's unit tests, or to audit unit test coverage for a specific module.
---

# Enrich frontend unit tests

Deepen `tests/unit/` coverage for whatever scope was described in this
invocation (a specific file, or a general audit if none was given).

Read `src/frontend/CLAUDE.md` first if you haven't already this session,
particularly the "Testing" section's list of harness gotchas — don't
rediscover those from scratch.

## What belongs in `tests/unit/`

Pure logic and hooks tested in isolation with **no full component render
and no MSW network mocking** — `src/lib/utils.ts`, `src/lib/env.ts`,
`src/lib/api.ts`'s interceptor logic, `src/proxy.ts`'s route-guard
function. If a test needs `render()` from React Testing Library or
touches the MSW `server`, it belongs in `tests/integration/` instead.

## Steps

1. **Pick the target.** If given a specific file, scope to that.
   Otherwise, survey `src/lib/`, `src/proxy.ts`, and any pure helper
   functions inside components (e.g. `formatDuration` in
   `StudentDashboard.tsx`) for thin or absent `tests/unit/` coverage.

2. **For each function, enumerate**: the happy path (already likely
   covered), boundary values (empty string, zero, empty array, exactly
   at a length/size limit), and negative/error cases (malformed input,
   missing optional fields, the function's own documented edge cases).
   `tests/unit/env.test.ts`'s handling of `window.__ENV__.NEXT_PUBLIC_API_URL`
   being an empty string vs. absent vs. present is the template for this
   — three distinct states that look similar but exercise different code
   paths.

3. **For `src/proxy.ts` specifically**, this is the single most
   security-critical file in the frontend (Critical Rule 2 — its
   misplacement once disabled all route protection silently for a whole
   session). Any change here deserves disproportionate test attention:
   every path in `PUBLIC_PATHS`, nested protected paths, the
   presence-vs-validity distinction (a garbage/expired cookie value must
   still pass — validation is the backend's job), and the matcher config
   itself.

4. **Write the tests**, following existing style: `describe` per
   function/module, one `it` per case, a comment only when the *why* of a
   case isn't obvious from its name (see `tests/unit/proxy.test.ts`'s
   "does not treat a path that merely starts with a public path as
   public" case).

5. **Verify via mutation, not just by running green.** Temporarily break
   the logic under test (invert a condition, remove a guard) and confirm
   the new test actually fails — then restore it and confirm the suite
   passes again. This project's `proxy.ts` tests were mutation-verified
   exactly this way (`git diff`-style manual revert, not a mutation
   testing tool) and it's the standard to match, not an optional extra.

6. **Run the full suite**, not just the new file:
   ```bash
   cd src/frontend && bun test
   ```
   A file passing in isolation has previously masked a cross-file issue
   (the MSW server lifecycle bug documented in `CLAUDE.md`) — always
   confirm against the whole suite before calling it done.

## Notes

- Don't add DOM rendering to a unit test to "make it easier" — if a test
  needs `render()`, that's a sign it belongs in `tests/integration/`
  instead, not a reason to import `@testing-library/react` into
  `tests/unit/`.
- A function with zero existing tests is worth investigating for *why* —
  `src/proxy.ts` had real live-app impact hiding behind "looks fine on
  read" before anyone actually tested it. Treat untested security- or
  auth-adjacent logic as higher priority than untested pure formatting
  helpers.

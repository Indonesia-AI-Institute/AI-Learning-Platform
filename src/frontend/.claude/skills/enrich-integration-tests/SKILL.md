---
name: enrich-integration-tests
description: Audit and deepen integration test coverage in tests/integration/ — untested components/hooks, the full loading/success/error/empty state matrix per data-fetching component, and MSW-mocked network edge cases. Use when asked to improve, expand, enrich, or add more detail to the frontend's integration tests, or to audit integration test coverage for a specific component.
---

# Enrich frontend integration tests

Deepen `tests/integration/` coverage for whatever scope was described in
this invocation (a specific component/hook, or a general audit if none
was given).

Read `src/frontend/CLAUDE.md` first if you haven't already this session,
particularly the "Testing" section — several non-obvious harness quirks
are already documented there (Radix `Select` double-rendering item text,
`mock.module` + dynamic import ordering, the zod-validation-message
rendering flakiness). Don't rediscover those from scratch, and don't
silently work around a *new* one without adding it to `CLAUDE.md` too.

## What belongs in `tests/integration/`

Anything that needs `render()` from React Testing Library — a component
or a hook exercised through real network calls mocked at the MSW
boundary (`tests/mocks/server.ts`/`handlers.ts`), not through a mocked
service module. Mocking `src/services/*.ts` directly would only prove a
mock got called; MSW proves the real hook → service → axios chain
actually produces the right request and handles the right response
shape.

## Steps

1. **Pick the target.** If given a specific component, scope to that.
   Otherwise, survey `src/hooks/`, `src/components/auth/`,
   `src/components/chat/`, and `src/components/dashboard/` for missing or
   thin coverage — check `find src/frontend/tests/integration -name "*.test.tsx"`
   against what actually exists in `src/components/`/`src/hooks/`.

2. **For a component that fetches data, cover the full state matrix**:
   loading (assert the actual loading UI, not just "doesn't crash"),
   success with data, success with an empty result (an empty array isn't
   the same as still-loading — `TeacherDashboard`'s "no classes yet" case
   is the template), and at least one error/failure response from the
   mocked endpoint.

3. **For a form, cover**: valid submission (redirect/success state),
   each validation rule defined in its zod schema, and the backend
   rejecting valid-looking input (e.g. "email already registered") —
   asserting the *functional* outcome (was the API called? did navigation
   happen?) is more reliable in this harness than asserting exact
   validation-message text for client-side zod errors specifically (see
   the CLAUDE.md note on this) — don't spend unbounded effort chasing
   that specific flakiness again without a real lead.

4. **For a mutation (login, chat send, create/update/delete), cover**:
   the in-flight state (button disabled, correct loading label), success,
   and failure — and for anything with a guard against double-submission
   or concurrent calls (see `useChat`'s "ignores a second send while
   streaming" test), a test that actually exercises the guard, not just
   the single-call path.

5. **Use MSW's `server.use(...)` for per-test overrides** rather than
   editing the shared default handlers in `tests/mocks/handlers.ts` —
   defaults should stay generically "happy path," with specific
   tests layering their own response via `server.use()` for the case
   they're testing. `server.resetHandlers()` runs after every test
   automatically (registered globally, see `CLAUDE.md`), so overrides
   never leak between tests.

6. **Run the full suite before calling it done:**
   ```bash
   cd src/frontend && bun test
   ```

## Notes

- A component with zero tests despite real conditional logic (multiple
  render branches, a query, a mutation) is worth flagging even if the
  invocation didn't specifically ask about it — untested conditional
  rendering is exactly where this codebase's real bugs have hidden
  (the `LoginForm` password-field label-association bug was only found
  while writing its first integration test, not during code review).
- Don't add a per-file MSW `beforeAll`/`afterAll` — see `CLAUDE.md` and
  the `test` skill for why that caused real, hard-to-diagnose failures.

---
name: test
description: Run the AI Learning Platform frontend's Bun test suite (unit and/or integration). Use when asked to run frontend tests, check if frontend changes broke anything, or verify a fix with the test suite.
---

# Frontend test suite

No database, no Docker container, no running dev server needed for any of
this — `tests/unit/` is pure logic and hooks with mocked network calls
(`src/proxy.ts`'s route guard is tested directly against real
`NextRequest` objects, still with zero I/O); `tests/integration/` renders
real components via React Testing Library and mocks the network boundary
with MSW.

## Steps

1. **Decide scope.** If the user just asked to "run the tests" with no
   qualifier, run everything (step 3, no path argument). If they're
   iterating on a single component/hook, run just that file for a fast
   loop, then the full suite once before calling it done — see the note
   in `CLAUDE.md` about a bug that only showed up running the *whole*
   suite together (an MSW server lifecycle conflict), not any single file
   in isolation.

2. **Install dependencies** if not already done (idempotent):
   ```bash
   cd src/frontend && bun install
   ```

3. **Run the suite:**
   ```bash
   cd src/frontend
   bun test                    # everything
   bun run test:unit           # tests/unit/ only
   bun run test:integration    # tests/integration/ only
   bun test tests/integration/LoginForm.test.tsx   # one file
   ```

4. **Report results plainly**: pass/fail counts, and for any failure the
   actual assertion output — don't summarize a failure away as "probably
   fine." If a test that used to pass now fails, that's a real regression
   to investigate, not a formatting issue.

5. **Always re-run the full `bun test` before declaring done**, even if
   you were only iterating on one file — cross-file state (the shared MSW
   server singleton, in particular) has caused failures that only
   appeared running everything together.

## If a test fails in a way that looks like the harness, not the code

Check `CLAUDE.md`'s "Testing" section first — several genuinely
non-obvious gotchas are already documented there (the `dom.setup.ts` /
`setup.ts` preload ordering requirement, `NextRequest` cookies needing
`.cookies.set()` instead of a constructor header once happy-dom's
`Headers` polyfill is active, Radix `Select` rendering item text twice,
`mock.module` + dynamic `import()` ordering for third-party modules like
`next/navigation`). Don't re-derive these from scratch — read that
section before concluding a failure means the app code is broken.

## Notes

- Don't add a per-file MSW `beforeAll(() => server.listen())` /
  `afterAll(() => server.close())` to a new integration test file — the
  lifecycle is already registered once, globally, in
  `tests/msw.setup.ts` via `bunfig.toml`'s preload. Duplicating it caused
  `ECONNREFUSED` failures when the full suite ran (one file's `afterAll`
  closing the shared server out from under another file's still-running
  tests) even though every file passed individually.
- If you're verifying a specific bug fix, prefer running just the
  relevant test file for a fast iteration loop, then run the full suite
  once before calling it done (see step 5).

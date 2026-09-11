---
name: check
description: Run the frontend's full comprehensive check — lint, production build, and the test suite, in that order, with a consolidated pass/fail report. Use when asked to do a final check, comprehensive check, or full verification of the frontend, before considering a change done, or before committing/opening a PR.
---

# Frontend comprehensive check

Three checks that each catch different things — none of them subsumes
the others. This codebase has hit real cases of each independently: a
type-safety hole ESLint flagged that `bun test` never would (`any`
scattered across error handlers), a `set-state-in-effect` error that
only `bun run lint` catches, and a `next.config.ts`/CSP change that
built fine but broke route protection, only caught by actually curling a
built container (outside this skill's scope — see `docker-smoke-test`
for that). Run all three; don't stop at the first one that's clean and
assume the rest are fine.

## Steps

1. **Install dependencies** if not already done (idempotent):
   ```bash
   cd src/frontend && bun install
   ```

2. **Lint:**
   ```bash
   bun run lint
   ```
   Report errors and warnings separately — an error fails the script
   (exit code 1) and must be fixed or deliberately justified; a warning
   doesn't block, but a NEW warning introduced by this change is still
   worth a second look, not an automatic pass. `no-explicit-any` errors
   in particular are worth fixing properly (a real derived type, not
   `unknown` used as a silence-the-linter escape hatch) rather than
   suppressed — see `src/lib/errors.ts` for the pattern used to eliminate
   a whole class of these (axios error handling) in one place instead of
   per call site.

3. **Build:**
   ```bash
   bun run build
   ```
   This runs Next's own TypeScript check over everything under `src/`
   (`tests/` is deliberately excluded in `tsconfig.json` — test files use
   Bun/jest-dom-specific globals the Next.js build environment doesn't
   know about). A build failure here after a clean lint pass usually
   means a type error ESLint's rules don't cover — don't skip this step
   just because lint was clean.

4. **Test:**
   ```bash
   bun test
   ```
   Always the full suite, not just files touched by the change — this
   project has a documented case (see `CLAUDE.md`) where every file
   passed individually but the full suite failed from a shared MSW server
   lifecycle conflict that only showed up running everything together.

5. **Report a consolidated result**: pass/fail for each of the three
   steps, and for any failure, the actual error output — not a summary
   that says "mostly fine." If all three are clean, say so plainly rather
   than padding the report.

## If something fails

- **Lint error**: fix it for real (see step 2) rather than adding an
  inline `eslint-disable` — the one standing exception in this codebase
  is `@next/next/no-location-assign-relative-destination` on `src/lib/api.ts`'s
  401 redirect guard, which is a deliberate hard-reload (clears all
  client state) and not something `useRouter().push()` would do.
- **Build failure with a passing lint**: almost always a type error in a
  file ESLint didn't fully type-check, or a Server/Client Component
  boundary issue. Read the actual `tsc` error — don't guess.
- **Test failure**: see the `test` skill and `CLAUDE.md`'s "Testing"
  section for this project's specific test-harness gotchas before
  assuming the application code itself is broken.

## Notes

- This skill doesn't build or run the Docker image — for that (and for
  verifying route protection / runtime env injection actually work in a
  real container, not just that the code compiles), use
  `docker-smoke-test` separately.
- Don't run these three checks out of order to "save time" by skipping
  ahead — a build or test failure can look identical whether or not lint
  was clean, but knowing which one actually failed (and whether the
  others would have too) is the point of running all three.

---
name: new-feature
description: Add a new resource or capability end-to-end across both backend and frontend — orchestrates each project's own scaffolding skills in the right order and makes sure neither half gets forgotten. Use when asked to add a new feature that needs both an API and a UI for it, not just a backend-only or frontend-only change.
---

# New full-stack feature

A thin orchestration layer over each project's own scaffolding skills —
the actual conventions for each piece live in those skills and in each
project's `CLAUDE.md`. This skill's job is sequencing and making sure
the frontend half doesn't get forgotten when a request is framed as "add
an endpoint for X" but clearly implies a UI too (or vice versa).

## When to use this vs. a single project's skill

If the request is unambiguously backend-only (an internal API another
service will call, a data migration) or frontend-only (a UI change
against an existing endpoint), just use that project's own skill
directly — `new-endpoint` or `new-page`/`new-component`/`new-hook`. Use
this one when a feature genuinely needs both, or when it's ambiguous
enough that sequencing matters.

## Steps

1. **Clarify the full shape of the feature before writing anything** —
   what data it needs, who can access it (student/teacher/both), and
   whether it's a new resource (new table) or behavior on an existing
   one. If any of this is unclear or a genuine product decision (e.g.
   "should students see this"), ask rather than assuming — this repo has
   deferred exactly these kinds of decisions before (see both `CLAUDE.md`
   files' "known gaps") rather than guessing at authorization scope.

2. **Backend first**, in this order — each step is its own skill:
   - New table needed → `new-model` (backend), then `db-migrate` to
     generate and review the migration.
   - `new-endpoint` (backend) for the schema/service/route/tests. This is
     where ownership scoping and auth dependencies get decided —
     get this right before the frontend has anything to call.
   - If the feature needs a new toggle/config value → `new-config-var`
     (backend).
   - Run the backend's own `test` skill before moving on — don't build
     the frontend half against an API that doesn't actually work yet.

3. **Frontend second**, in this order:
   - `new-service` (frontend) — the axios wrapper calling the new
     endpoint(s). Confirm the exact request/response shape against what
     the backend schema actually defines, not what was assumed while
     planning.
   - `new-hook` (frontend) if the data-fetching/mutation logic is reused
     or complex enough to warrant it; otherwise call the service directly
     from a `useQuery`/`useMutation` in the page.
   - `new-page` or `new-component` (frontend) for the UI itself.
   - Run the frontend's own `check` skill before moving on.

4. **Verify the integration for real**, not just that each side's own
   tests pass — either manually via `full-stack-dev` (bring up the whole
   stack, click through the actual flow) or, for something worth a
   permanent regression test, an integration test on the frontend side
   that hits the real new endpoint through MSW with the actual
   request/response shape the backend defines.

5. **Run `full-stack-check`** before considering the feature done.

## Notes

- Don't let the frontend and backend halves diverge on the data shape —
  if the backend schema changes after the frontend service was written
  against an earlier version, update the frontend type too; these aren't
  automatically kept in sync.
- A feature that only got a backend half when the request implied a UI
  too (or vice versa) is an incomplete delivery, not a smaller one worth
  shipping first without saying so — if intentionally splitting the work
  into two PRs, say that explicitly rather than silently stopping halfway.

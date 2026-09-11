---
name: modularize
description: Find and extract reusable components, hooks, or services out of page files that have grown large or duplicated — without changing behavior. Use when asked to modularize, refactor, clean up, or de-duplicate frontend pages/components, or when a page.tsx has accumulated inline logic that belongs elsewhere.
---

# Modularize frontend code

Extraction, not redesign: the goal is the same behavior in a better
place, verified before and after — never bundled with an unrelated
behavior change. If you find a real bug while doing this, fix it as a
separate, called-out step, not silently folded into the extraction.

## Finding real candidates

Don't extract speculatively — "this component only has one caller and
isn't complicated" is a sign to leave it alone. Look for:

- **The same JSX block appearing in 2+ page files.** A concrete, already
  spotted example in this codebase: the loading-spinner block
  (`<div className="w-5 h-5 border-2 border-primary border-t-transparent
  rounded-full animate-spin" />` plus a "Loading..." label) is
  hand-copied across several `(dashboard)/**/page.tsx` files with minor
  variation. That's a real `<LoadingSpinner />` or `<PageLoading />`
  candidate — search for `animate-spin` across `src/app/` to find every
  occurrence before deciding on the extracted component's exact props
  (size, label text vary slightly between call sites; the extraction
  needs to cover the real variation, not just the first instance found).
- **The same data-fetching `useQuery`/`useMutation` call (same query key,
  same service method) appearing in more than one component.** That's a
  `new-hook` candidate — check the query key naming is already consistent
  between the call sites before extracting (if it isn't, that's itself
  worth flagging).
- **Inline `api`/service calls inside a component** instead of going
  through `src/services/*.ts` — extract to a service method first (see
  `new-service`), independent of whether the surrounding logic also
  becomes a hook.
- **A page component whose `render`/JSX body is long enough that its own
  structure is hard to see** (deeply nested conditionals, several
  unrelated sections) — even with zero duplication elsewhere, splitting
  it into named sub-components *within the same file or a colocated file*
  can be worth it, but only when it genuinely clarifies the structure,
  not as a mechanical line-count reduction.

## Steps

1. **Pick one candidate at a time.** Don't batch unrelated extractions
   into one change — each should be independently reviewable and
   revertable.

2. **Run the full test suite first** (`bun test` from `src/frontend/`) as
   a baseline — note the pass count. If the piece being extracted has no
   existing test coverage, that's worth fixing as part of this (a
   refactor with no regression coverage is a refactor you can't verify),
   but write the test against the *current* behavior before moving code,
   so it's a genuine regression guard rather than a test written to match
   whatever the refactor produces.

3. **Extract to the right place**, per the existing convention (each has
   its own skill with the full pattern):
   - Repeated JSX → `src/components/<domain>/` (see `new-component`).
   - Repeated or complex stateful/data logic → `src/hooks/` (see
     `new-hook`).
   - Inline API calls → `src/services/*.ts` (see `new-service`).

4. **Keep props/parameters minimal and specific to what's actually used
   across the real call sites** you found — don't add speculative
   flexibility (a `variant` prop, an optional callback) for a use case
   that doesn't exist yet at any current call site.

5. **Update every call site**, not just the first one found — re-run the
   search from "Finding real candidates" after extracting to confirm none
   were missed.

6. **Run the full test suite again** and confirm the same pass count (or
   higher, if you added coverage in step 2) — a change in behavior at
   this point means the extraction wasn't behavior-preserving, which
   needs to be resolved before moving on, not shipped as a "small
   improvement while I was in there."

7. **Run `bun run build`** — a page that was implicitly relying on
   something about its own file (a type inferred in-place, a Server vs.
   Client Component boundary) can break in ways `bun test` alone won't
   catch if the extraction crossed that boundary.

## Notes

- An extraction that changes a prop's type, adds a new required prop with
  no default, or changes what a callback receives is an API change to
  every call site — treat it with the same care as changing a public
  function signature, not as an internal-only refactor.
- If two "duplicate" blocks turn out to have a subtle difference once you
  look closely (different loading label text, a slightly different size),
  decide deliberately whether that's a real variation the extracted
  component/hook needs to support (a prop) or an inconsistency worth
  fixing to be identical — don't silently pick one and drop the
  difference.

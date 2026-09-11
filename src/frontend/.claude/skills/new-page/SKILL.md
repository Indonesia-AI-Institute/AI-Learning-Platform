---
name: new-page
description: Scaffold a new protected page (route, service method, hook, component) following this frontend's existing conventions — data fetching via TanStack Query, service-layer axios calls, shadcn/ui components. Use when asked to add a new page, route, or screen to the frontend.
---

# New frontend page

Scaffolds a new page under `src/app/(dashboard)/` following the patterns
already established by the existing pages, rather than inventing a new
structure.

## Steps

1. **Confirm the route and its auth requirements.** Almost everything
   under `(dashboard)` is protected by `src/proxy.ts`'s presence-only
   cookie check by default (see `CLAUDE.md` Critical Rule 2) — a new page
   there needs no extra wiring for that. If the page should be public,
   it needs to go under `(auth)` instead (or be added to
   `PUBLIC_PATHS` in `src/proxy.ts`, which should be a deliberate,
   explicit decision, confirmed with the user).

2. **Identify the backend endpoint(s) this page needs.** Check
   `src/services/*.ts` for an existing service method that already covers
   it before adding a new one — most CRUD operations per resource already
   exist. If a new service method is genuinely needed, add it to the
   relevant `src/services/<resource>.service.ts` file (or create a new
   one, matching the existing thin-wrapper style — one async function per
   endpoint, no logic beyond the axios call).

3. **Add or reuse a hook** in `src/hooks/` if the data-fetching logic is
   used in more than one place, or needs local state beyond what
   `useQuery`/`useMutation` alone provides (see `useChat.ts`,
   `useCurrentUser.ts` for examples of each). For a single-use query, it's
   fine to call `useQuery` directly in the page component — not every
   query needs its own hook file.

4. **Build the page component** under `src/app/(dashboard)/<route>/page.tsx`.
   Wrap content in `DashboardLayout` (`src/components/layout/DashboardLayout.tsx`)
   for the sidebar/navbar chrome, matching every other dashboard page.
   Use `src/components/ui/*` (shadcn primitives) for form/layout elements
   rather than hand-rolling new ones.

5. **Handle loading and error states explicitly** — every existing
   `useQuery` call in this codebase branches on `isLoading` before
   rendering data; don't let a page flash undefined/null content.

6. **If the page has a form**, follow the `react-hook-form` + `zod` +
   `components/ui/form.tsx` pattern used by `LoginForm`/`RegisterForm`.
   **Read Critical Rule 5 in `CLAUDE.md` before adding any input with a
   sibling icon/button** (password-visibility toggles, clear buttons,
   etc.) — `FormControl` must wrap the input directly, never a wrapping
   `<div>`, or the label loses its accessible association.

7. **Write tests.** A page with real logic (conditional rendering,
   mutations, navigation) should get an integration test under
   `tests/integration/`, following the MSW-mocked-network pattern used by
   `StudentDashboard.test.tsx`/`TeacherDashboard.test.tsx` — not a
   service-module mock. Run `/test` before considering the page done.

## Notes

- Don't add a new top-level layout or duplicate `DashboardLayout`'s
  sidebar/navbar composition — extend the existing one if it's missing
  something, rather than building a page-specific alternative.
- Server Components are the default in `src/app/`; only add `"use client"`
  where actually needed (state, effects, event handlers, or a hook that
  itself needs it) — most existing page components are already marked
  `"use client"` because they use hooks, but don't cargo-cult the
  directive onto a page that doesn't need it.

---
name: new-hook
description: Scaffold a new hook in src/hooks/, following this frontend's conventions — a thin TanStack Query wrapper for simple data fetching, or a stateful hook (refs, effects, manual fetch) for anything more involved like useChat. Use when asked to add a new hook, or to extract data-fetching/stateful logic out of a component into a reusable hook.
---

# New frontend hook

Adds a new `src/hooks/use<Thing>.ts` hook, matching one of the two
patterns every existing hook already follows.

## Steps

1. **Decide whether this needs a dedicated hook file at all.** A
   `useQuery`/`useMutation` call used in exactly one component doesn't
   need to be extracted — see `TeacherDashboard.tsx`/`StudentDashboard.tsx`,
   which call `useQuery` directly rather than wrapping it. Extract to
   `src/hooks/` only when the logic is reused across components, or
   carries enough local state/effects that inlining it would clutter the
   component (see `useChat.ts` for the latter case).

2. **Pick the right pattern:**
   - **Thin query/mutation wrapper** (`useAuth.ts`, `useCurrentUser.ts`):
     wraps one or more `useQuery`/`useMutation` calls around a
     `src/services/*.ts` method, adds `onSuccess`/`onError` side effects
     (navigation, cache invalidation), returns a flat object of state +
     actions. Use this when the hook's job is "fetch/mutate this resource
     and react to the result."
   - **Stateful hook** (`useChat.ts`): owns `useState`/`useRef`/`useEffect`
     directly, for logic that doesn't fit the query/mutation shape (manual
     streaming, imperative cleanup on unmount, refs to dodge stale
     closures). Use this when TanStack Query's request/response model
     doesn't match what the hook actually does.

3. **If the hook needs the current user or auth state**, use
   `useCurrentUser()` — don't add a second way to determine who's logged
   in (see `CLAUDE.md` Critical Rule 4: auth state lives only in the
   httpOnly cookie, fetched fresh via `GET /auth/me`, never cached
   client-side outside TanStack Query's own cache).

4. **If the hook calls the backend**, go through a `src/services/*.ts`
   method — never call `api` (`src/lib/api.ts`) directly from a hook. If
   the service method doesn't exist yet, use the `new-service` skill
   first.

5. **Name query keys consistently** with what's already used for that
   resource elsewhere (`["currentUser"]`, `["myClasses"]`,
   `["chatHistory", sessionId]`, etc.) — a new hook that duplicates an
   existing resource under a different key fragments the cache and breaks
   `invalidateQueries` calls elsewhere that target the established key.

6. **Write tests** under `tests/integration/` (a hook test needs
   `renderHook` from React Testing Library, which puts it in the
   integration tier by this codebase's convention — see `CLAUDE.md`'s
   Testing section) with MSW mocking whatever endpoint the hook's
   service call hits. Follow `tests/integration/useAuth.test.tsx` or
   `useChat.test.tsx` as the template depending on which pattern you
   used in step 2. If the hook needs `next/navigation`'s `useRouter`,
   use the `mock.module(...)` + dynamic `await import(...)` pattern
   documented in `CLAUDE.md` — a static import resolves the real router
   first and the mock never takes effect.

## Notes

- Don't put business logic in the hook that belongs in a service or the
  backend — a hook orchestrates state and side effects around a
  service call; it shouldn't itself decide what's valid or transform
  response shapes beyond what the component needs to render.
- If the hook manages a resource with a cleanup requirement (an open
  connection, a session that needs to be ended, an in-flight request that
  should abort on unmount), follow `useChat.ts`'s ref pattern — refs, not
  state, inside an unmount effect, so the cleanup always reads the latest
  value instead of the one captured when the effect first ran.

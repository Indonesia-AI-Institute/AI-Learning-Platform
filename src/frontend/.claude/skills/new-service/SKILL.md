---
name: new-service
description: Scaffold a new service file (or add a method to an existing one) in src/services/, following this frontend's thin-axios-wrapper convention — one async function per backend endpoint, no business logic. Use when asked to add a new API service, service method, or wire up a new backend endpoint on the frontend.
---

# New frontend service

Adds a new `src/services/<resource>.service.ts` file, or a method to an
existing one, matching the pattern every other service in this codebase
already follows.

## Steps

1. **Check whether a service for this resource already exists** in
   `src/services/`. Most CRUD operations for `auth`, `chat`, `class`,
   `course`, `enrollment`, `task`, `user`, and `analytics` are already
   covered — add a method to the existing file rather than creating a
   duplicate for the same backend resource.

2. **Confirm the exact backend route** (path, HTTP method, request/response
   shape) before writing the call — check `src/backend/api/v1/*_routes.py`
   if this repo has the backend checked out alongside, or ask rather than
   guessing the path. A wrong path fails silently at runtime, not at
   compile time — TypeScript can't catch a typo'd URL string.

3. **Add the corresponding types** to `src/types/<resource>.types.ts` if
   they don't already exist, mirroring the backend's response schema.
   Reuse existing types rather than redeclaring near-duplicates.

4. **Write the service method**, matching the existing thin-wrapper style
   exactly — no business logic, no error handling beyond what the shared
   `api` instance's interceptor already provides:
   ```ts
   import api from "@/lib/api";
   import { Thing } from "@/types/thing.types";

   export const thingService = {
     getById: async (id: string): Promise<Thing> => {
       const response = await api.get<Thing>(`/things/${id}`);
       return response.data;
     },
   };
   ```
   Every existing service follows this: an exported plain object, each
   property an `async` arrow function, one backend call per function,
   `response.data` returned directly (never the raw axios response).

5. **Don't call the service directly from a page component for anything
   reused more than once, or anything needing loading/error state** —
   wrap it in a `useQuery`/`useMutation` hook instead (either inline in
   the component for a single use, or a dedicated file in `src/hooks/`
   if reused — see `CLAUDE.md`'s directory map for examples of each).

6. **Write tests.** A new service method has no logic worth a dedicated
   unit test on its own (it's a pure passthrough) — instead, test it
   indirectly through whatever hook or component actually calls it, using
   MSW to mock the real HTTP call (see `tests/integration/`, and the
   `enrich-integration-tests` skill). Add an MSW handler for the new
   endpoint to `tests/mocks/handlers.ts` if other tests are likely to need
   it too; otherwise a per-test `server.use(...)` override is enough.

## Notes

- Don't add try/catch inside a service method to swallow or transform
  errors — let them propagate to the calling hook/component. The shared
  `api` instance's interceptor already handles the one cross-cutting
  concern (401 → redirect to `/login`); anything more specific belongs in
  the caller, which has the context to decide what a failure means for
  that particular UI.
- Don't add authentication headers or tokens manually — `withCredentials:
  true` on the shared `api` instance already sends the httpOnly cookie on
  every request (see `CLAUDE.md` Critical Rule 4).

# Frontend — AI Learning Platform

Next.js 16 (App Router) + React 19 + TypeScript frontend for an AI-tutoring
platform. Teachers manage courses/classes/tasks; students chat with an LLM
through session-based chat tied to a task. Auth is JWT via an httpOnly
cookie — the frontend never sees or stores the token itself.

This file is project memory for whoever (human or Claude) works in this
directory. It leans heavily on lessons from real bugs found and fixed here
— follow the "Critical rules" section literally, they exist because
violating them already caused production-shaped bugs once.

## Architecture

```
src/app/(auth)/*        public routes: /login, /register
src/app/(dashboard)/*   everything else — protected by src/proxy.ts
src/proxy.ts            route guard (Next 16 renamed "middleware" to "proxy")
src/hooks/               data-fetching + mutation hooks (TanStack Query)
src/services/            thin per-resource axios wrappers, one file per API resource
src/lib/api.ts            the shared axios instance + 401 redirect guard
src/lib/env.ts            getApiUrl() — runtime vs build-time API URL resolution
src/components/ui/       shadcn/ui primitives (Radix-based)
src/components/          feature components, grouped by domain (auth/, chat/, dashboard/, layout/)
src/types/                TypeScript types mirroring backend schemas
```

Data flow: `page.tsx` (Server or Client Component) → a hook in `src/hooks/`
(wraps `useQuery`/`useMutation`) → a service in `src/services/` (thin axios
call) → the shared `api` instance in `src/lib/api.ts` → backend, whose base
URL is resolved by `getApiUrl()`.

## Critical rules (each exists because breaking it already caused a bug)

**1. Never read `process.env.NEXT_PUBLIC_API_URL` in client-side code —
always call `getApiUrl()` (`src/lib/env.ts`).** Next.js inlines
`NEXT_PUBLIC_*` vars into the client bundle at *build time*. This image is
deliberately built without that var set (see rule 3), so any direct
reference compiles to a literal `"undefined"` baked into the shipped JS —
unfixable without a rebuild. `useChat.ts` shipped with exactly this bug
(two raw `process.env.NEXT_PUBLIC_API_URL` references), which silently
broke chat streaming in every production container. `getApiUrl()` reads
`window.__ENV__` instead, which `entrypoint.sh` writes into
`public/env-config.js` fresh at every container *start*, so the same
image works unmodified across environments.

**2. The route-guard file is `src/proxy.ts`, exporting a function named
`proxy` — not `middleware.ts` / `export function middleware`.** Next.js
16 deprecated and renamed the "middleware" convention to "proxy" (see
[migration guide](https://nextjs.org/docs/app/api-reference/file-conventions/proxy#migration-to-proxy)).
This repo actually shipped a `middleware.ts` at the wrong location
entirely (`src/frontend/middleware.ts`, sibling to `package.json`, not
`src/middleware.ts` sibling to `src/app`) for an entire session — Next
never loaded it, so **every unauthenticated visitor could reach every
protected page's shell with zero redirect**, silently, because the file
looked correct on inspection. If you ever add a second proxy-like file or
move this one, verify the fix live: build the image, curl a protected
path with no cookie, confirm a 307 to `/login`.

**3. `PORT` is runtime-only — no build-time default, no `EXPOSE` in the
Dockerfile. `HOSTNAME` is force-set to `0.0.0.0` in `entrypoint.sh`, not
left configurable.** Docker/Linux auto-populates `HOSTNAME` with the
container ID *before* any entrypoint script runs, so a
`${HOSTNAME:-0.0.0.0}` fallback pattern (which works fine for `PORT`)
silently never triggers for `HOSTNAME` — the app would bind to whatever
IP that container-ID hostname resolves to instead of all interfaces,
making it unreachable from its own healthcheck. There is no legitimate
reason to bind to anything other than all interfaces inside a container,
so this is an unconditional `export HOSTNAME=0.0.0.0`, not a fallback.

**4. Auth state lives only in the httpOnly cookie — never
`localStorage`/`sessionStorage`, never a client-side auth store holding a
token.** A `Zustand` auth store existed here with `user`/`isAuthenticated`
state and was never actually wired to anything (`setUser` was called
nowhere in the app) — dead code left over from an earlier design that was
correctly abandoned in favor of the cookie being the sole source of
truth. If you need "is this user logged in," fetch it (`useCurrentUser`,
which hits `GET /auth/me`); don't cache a boolean client-side.

**5. In `components/ui/form.tsx`-based forms, `FormControl` must wrap the
actual input element directly — never a wrapping `<div>`.** `FormControl`
uses Radix `Slot` to clone `id`/`aria-describedby`/`aria-invalid` onto its
*single child*. `LoginForm`'s password field wrapped `FormControl` around
a `<div className="relative">` (to position the show/hide-password
button), which sent those attributes to the div instead of the `<input>`
— the `<label>`'s `htmlFor` pointed at an id the real input never had,
breaking the accessible name entirely (caught by `getByLabelText` failing
in `tests/integration/LoginForm.test.tsx`). If an input needs a sibling
overlay element (an icon button, a suffix), put the wrapping `<div>`
*outside* `FormControl`, with `FormControl` wrapping only the `Input`:
```tsx
<div className="relative">
  <FormControl><Input className="pr-10" {...field} /></FormControl>
  <button className="absolute ...">...</button>
</div>
```

**6. `package.json`'s `trustedDependencies` must only list packages
actually present in `bun.lock`.** It had a stale `"msw"` entry (a leftover
from an earlier pnpm `.npmrc` config, carried over uncritically during
the pnpm→Bun migration) even though `msw` wasn't in the dependency tree
at all until this session's test suite added it for real. A stale entry
here is harmless to Bun itself but is misleading, unreviewed config —
when adding a new one, confirm the package is real via `grep <name>
bun.lock` first.

**7. Package manager is Bun, exclusively — no `pnpm-lock.yaml`,
`pnpm-workspace.yaml`, `.npmrc`, or `package-lock.json` should ever
reappear.** This project migrated from pnpm to Bun end-to-end (Dockerfile,
`entrypoint.sh`, lockfile). A `pnpm-workspace.yaml` survived the
migration completely undetected for a while — it doesn't contain the
literal string "pnpm" in its own content, so a `grep -r pnpm .` swept the
repo clean while missing it by filename alone. If auditing for
leftover-package-manager cruft, search by filename too:
`find . -iname "*pnpm*" -o -iname "*.npmrc"`.

**8. The CSP in `next.config.ts` allows `'unsafe-inline'` on `script-src`
— this is a deliberate, considered tradeoff, not an oversight.** A
nonce-based strict `script-src` was tried first; Next's App Router only
applies a request's nonce automatically if it reads it back out of the
`Content-Security-Policy` *request* header (set in `proxy.ts`, not
`next.config.ts`), and doing that correctly requires **every page to
render dynamically** — no more static prerendering — plus the mechanism
is still marked experimental. Given this app has no
`dangerouslySetInnerHTML`/`rehype-raw` anywhere (verified), CSP here is
defense-in-depth on top of React's default escaping, not the only layer,
so the tradeoff favors keeping static generation. Revisit if Next
stabilizes nonce support without the dynamic-rendering cost.

**9. The root `.env` (from `.env.example`) is a different file from
`.env.fe`/`.env.be`, with a different job.** `docker compose`'s own
`${VAR}` interpolation (used for `API_PORT`/`FRONTEND_PORT` host-mapping
and reads nothing from `env_file:` entries — those are injected into the
*container*, a separate mechanism that happens after Compose has already
resolved the compose file's own placeholders. Setting `PORT` in `.env.fe`
alone will not change the host-side port mapping; both need to move
together, which is why the compose files also thread `API_PORT`/
`FRONTEND_PORT` into each container's own `PORT` env var via an explicit
`environment:` block, overriding `env_file`'s value so the two can't
drift out of sync.

## Directory map

| Path | What's there |
|---|---|
| `src/app/(auth)/{login,register}/page.tsx` | Public pages |
| `src/app/(dashboard)/**/page.tsx` | Protected pages — courses, classes, tasks, chat, analytics |
| `src/proxy.ts` | Route guard — presence-only cookie check, see Critical Rule 2 |
| `src/hooks/useAuth.ts` | login/register/logout mutations |
| `src/hooks/useCurrentUser.ts` | `GET /auth/me`, cached, no refetch-on-focus (avoids 401 redirect loops) |
| `src/hooks/useChat.ts` | Manual SSE-style streaming over raw `fetch` (not axios) — see its own comments for the abort/unmount handling |
| `src/services/*.ts` | One file per backend resource, each a thin object of axios calls — no business logic lives here |
| `src/lib/api.ts` | Shared axios instance; response interceptor redirects to `/login` on 401, guarded against redirect loops |
| `src/lib/env.ts` | `getApiUrl()` — see Critical Rule 1 |
| `src/lib/utils.ts` | `cn()` — clsx + tailwind-merge |
| `src/components/ui/` | shadcn/ui primitives — generally no business logic, safe to treat as a black box |
| `src/components/auth/` | `LoginForm`, `RegisterForm` — react-hook-form + zod |
| `src/components/chat/` | `ChatInput`, `ChatMessage`, `ChatHeader`, `StreamingMessage` |
| `src/components/dashboard/` | `StudentDashboard`, `TeacherDashboard`, `StatCard` |
| `src/components/layout/` | `DashboardLayout`, `Navbar`, `Sidebar` |
| `entrypoint.sh` | Generates `public/env-config.js` from runtime env, then `exec bun server.js` |
| `tests/` | Bun test suite — `unit/` and `integration/`, see "Testing" below |

## Running locally

```bash
cd src/frontend
bun install

# Configure environment (from the repo root)
cd ../..
cp .env.fe.example .env.fe
# edit .env.fe — NEXT_PUBLIC_API_URL should point at your running backend

cd src/frontend
bun run dev
```

The app is now at `http://localhost:3000`. See the repo root `README.md`
for running the full stack (frontend + backend + Postgres) via Docker
Compose instead.

## Testing

```bash
cd src/frontend
bun test              # everything
bun run test:unit     # tests/unit/ only
bun run test:integration  # tests/integration/ only
bun test --watch
```

No database, no Docker container needed for any of it — `tests/unit/`
tests pure logic and hooks with no network calls (except the
security-critical `src/proxy.ts` route guard, tested directly against
real `NextRequest` objects); `tests/integration/` renders real components
with React Testing Library and mocks the network boundary with
[MSW](https://mswjs.io) rather than mocking service modules — this
verifies hook → service → axios → (mocked) HTTP actually wires up
correctly, not just that a mocked function got called.

**Test infrastructure, if you're touching it:**
- `bunfig.toml`'s `[test] preload` lists three files, **in this exact
  order**: `tests/dom.setup.ts` (registers happy-dom's global
  `window`/`document` — must import nothing else, see its own comment for
  why), `tests/setup.ts` (jest-dom matchers + RTL `afterEach(cleanup)`),
  `tests/msw.setup.ts` (the MSW server lifecycle). Reordering the first
  two breaks every component test (`@testing-library/dom`'s `screen`
  binds to `document` at *its own* module-load time, which ES import
  hoisting would put before a same-file `GlobalRegistrator.register()`
  call).
- MSW's `server` (`tests/mocks/server.ts`) is a **shared singleton** —
  its `listen()`/`close()` lifecycle is registered exactly once, globally,
  in `tests/msw.setup.ts`. Do not add a per-file
  `beforeAll(() => server.listen())` in an integration test — that
  actually happened here once, and running the suite one file at a time
  (each file's own `beforeAll`/`afterAll` closing and reopening the same
  singleton) passed, while running the *whole* suite together produced
  `ECONNREFUSED` failures, because one file's `afterAll(close)` could fire
  while another file's tests were still relying on the server being open.
  Always verify test changes against the full `bun test`, not just the
  file you touched.
- Mocking a third-party module (e.g. `next/navigation`'s `useRouter`)
  needs `mock.module("next/navigation", () => ({...}))` called *before* a
  **dynamic** `await import(...)` of the component/hook under test — a
  static top-of-file `import` is hoisted above the `mock.module` call
  and resolves the real module first. Every test file that needs a
  router mock in this suite follows this pattern; copy it rather than
  using a static import.
- `NextRequest`'s constructor `headers: { cookie: "..." }` option
  silently doesn't work once `tests/dom.setup.ts` has registered
  happy-dom's global `Headers` polyfill (it shadows the platform's own,
  which `next/server` expects) — set cookies via
  `request.cookies.set(name, value)` after construction instead (see
  `tests/unit/proxy.test.ts`).
- Radix `Select`/`SelectItem` renders its item text **twice** (a hidden
  measurement copy plus the real, interactive option) — happy-dom doesn't
  compute layout well enough for jest-dom's visibility checks to filter
  the hidden one out, so a bare `getByText("Teacher")` throws "found
  multiple elements." Query `getByRole("option", { name: "Teacher" })`
  instead — it correctly resolves to only the real one.
- Asserting the exact rendered text of a client-side zod validation error
  (`FormMessage`'s content) was flaky in this specific React 19 +
  react-hook-form 7 + `@hookform/resolvers` 5 + zod 4 + happy-dom
  combination for reasons not fully root-caused — `handleSubmit` reliably
  blocked submission (verified independently), but the `FormMessage`
  component sometimes didn't re-render to show it in this harness. The
  existing form tests assert the *functional* outcome (no API call made)
  for this reason. If you get a clean repro of the exact trigger, it's
  worth revisiting — but don't spend unbounded time on it; assert
  function over form text where this shows up again.

## Docker

- `Dockerfile` is a 3-stage Bun build (`oven/bun:1.4.2-alpine`, pinned
  exact patch, not the floating `1-alpine` tag) — `bun install
  --frozen-lockfile`, `bun run build`, then a minimal runner stage
  copying only `.next/standalone`, `.next/static`, and `public/`.
- `entrypoint.sh` generates `public/env-config.js` from the container's
  runtime env, then `exec bun server.js` (Next's standalone server runs
  fine directly under Bun — verified live, not just built).
- No `EXPOSE`, no build-time `PORT`/`HOSTNAME` — see Critical Rules 1 and 3.
- `HEALTHCHECK` curls `http://localhost:${PORT:-3000}/`.
- Root `docker-compose.yml` builds this image locally (dev). Root
  `docker-compose.prod.yml` pulls the prebuilt
  `ghcr.io/indonesia-ai-institute/ai-learning-platform-frontend:${IMAGE_TAG:-latest}`
  image — see Critical Rule 9 for how host port mapping is wired there.

## Known, deliberately deferred gaps

Don't "fix" these without a product decision — they were evaluated and
explicitly left as-is:

- **`RegisterForm`'s role dropdown lets any anonymous visitor register as
  `teacher`** directly, with no invite/approval flow — a teacher account
  gets full course/class/task-creation rights and (correctly
  ownership-scoped, per the backend's own rules) access to their own
  students' analytics. This is a backend authorization-policy decision,
  not a frontend bug; `tests/integration/RegisterForm.test.tsx` has a
  test that documents the current behavior rather than assuming it's
  wrong.
- **No middleware/proxy-level JWT *validation*, only presence.**
  `src/proxy.ts` checks that an `access_token` cookie exists, not that
  it's a currently-valid, unexpired JWT — it structurally can't do more,
  since the signing secret is backend-only and must never reach the
  Edge/Node runtime this file executes in. The backend's own auth checks
  (`api/deps.py` on that side of the repo) remain the actual
  authorization boundary; this file only avoids showing a protected
  page's shell to a visitor with no session at all.
- **CSP `connect-src` is `*`**, not scoped to the API's real origin —
  `NEXT_PUBLIC_API_URL` is resolved at container runtime (Critical Rule
  1), so it isn't known at the `next.config.ts` build-time when the CSP
  header is assembled. A per-deployment fix (baking the real API origin
  into `connect-src` via `entrypoint.sh` rewriting a placeholder, similar
  to how `env-config.js` is generated) is possible but wasn't judged
  worth the added moving part yet.

## Conventions

- Commit messages follow Angular/conventional-commit style
  (`feat|fix|perf|refactor|docs|style|test|chore|ci|build|revert: ...`).
- No comments that just restate the next line. A comment earns its place
  by explaining a non-obvious *why* — a library quirk, a workaround for a
  specific bug, a tradeoff that isn't obvious from the code alone. Several
  comments in this codebase (`src/lib/env.ts`, `src/proxy.ts`,
  `entrypoint.sh`) are exactly that; match that bar, not decorative
  section banners.
- Services (`src/services/*.ts`) stay thin — one async function per
  endpoint, no business logic, no error handling beyond what axios/the
  interceptor already does. Business logic belongs in a hook or the
  backend, not here.

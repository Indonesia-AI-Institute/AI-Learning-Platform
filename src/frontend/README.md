# AI Learning Platform — Frontend

Next.js 16 (App Router) + React 19 frontend for the AI Learning Platform:
course/class/task views for teachers, session-based AI tutoring chat for
students, and prompt analytics dashboards that surface *how* students are
using that chat. TanStack Query for server-state, react-hook-form + zod
for forms, shadcn/ui (Radix) for components, JWT auth via an httpOnly
cookie the frontend never touches directly.

Two things are worth understanding before touching this codebase, both
covered below: **the route guard** (`src/proxy.ts`) that gates every
protected page, and **runtime API URL resolution** (`src/lib/env.ts`) —
the same Docker image is meant to run unmodified in any environment, which
means the backend's URL can't be baked in at build time. See
[Architecture & data flow](#architecture--data-flow).

For full-stack setup (frontend + backend together, Docker Compose,
one-shot deployment), see the [repo root README](../../README.md). This
file covers working on the frontend on its own.

## Tech stack

| Component | Technology |
|---|---|
| Framework | Next.js 16 (App Router) |
| UI | React 19 |
| Language | TypeScript |
| Styling | Tailwind CSS v4 |
| Components | shadcn/ui (Radix primitives) |
| Server state | TanStack Query |
| Forms | react-hook-form + zod |
| HTTP client | axios |
| Package manager / runtime | [Bun](https://bun.sh) |
| Tests | `bun test` + React Testing Library + MSW |

## Architecture & data flow

Most pages follow the same four-layer path from render to network:

```
page.tsx (Server or Client Component)
       │
       ▼
src/hooks/*.ts        A hook wraps TanStack Query's useQuery/useMutation
       │               (or, for chat, its own manual state — see below)
       ▼
src/services/*.ts      One thin object of axios calls per backend resource —
                       no business logic lives here, just the HTTP call
       │
       ▼
src/lib/api.ts          The shared axios instance — a response interceptor
                       redirects to /login on 401, guarded against loops
       │
       ▼
Backend API, base URL resolved by getApiUrl() (src/lib/env.ts)
```

**Every protected route is gated by `src/proxy.ts`** (Next.js 16 renamed
the old `middleware.ts` convention to `proxy.ts` — this file must live at
`src/proxy.ts`, exporting a function named `proxy`, or Next silently never
loads it and every protected page's shell becomes reachable with zero
redirect). It only checks that an `access_token` cookie is *present* —
it structurally can't validate the JWT itself, since the signing secret is
backend-only and must never reach this Edge/Node runtime. Real
authorization happens on the backend; this file only stops an
unauthenticated visitor from seeing a protected page's shell at all.

**The API URL is resolved at container runtime, not build time.** Next.js
normally inlines `NEXT_PUBLIC_*` vars into the client bundle when you run
`next build` — but this image is deliberately built with no API URL set,
so every client-side call goes through `getApiUrl()` (`src/lib/env.ts`),
which reads `window.__ENV__` instead. `entrypoint.sh` writes that object
into `public/env-config.js` fresh every time the container *starts*,
which is what lets one built image move between dev/staging/prod without
a rebuild — see `CLAUDE.md` Critical Rule 1. **Never** read
`process.env.NEXT_PUBLIC_API_URL` directly in client-side code; it will
compile to the literal string `"undefined"`.

**Chat streaming doesn't go through the `axios`/service layer at all.**
`src/hooks/useChat.ts` calls `fetch()` directly against
`${getApiUrl()}/chat/sessions/{id}/stream` with `credentials: "include"`
(so the auth cookie rides along) and reads the response body as an SSE-style
token stream, appending to a `streamingContent` state as chunks arrive.
It also registers a cleanup effect that fires `POST .../auto-end` when a
student navigates away mid-session, using refs (not state) so the
unmount handler always sees the latest `sessionId`/`isSessionActive`
rather than a stale closure.

## Project layout

```
src/app/(auth)/          public routes: /login, /register
src/app/(dashboard)/     protected routes — courses, classes, tasks, chat, analytics
src/proxy.ts             route guard (Next 16's renamed "middleware")
src/hooks/               data-fetching + mutation hooks (TanStack Query)
src/services/            thin per-resource axios wrappers
src/lib/                 shared axios instance, runtime API URL resolution, utils
src/components/ui/       shadcn/ui primitives
src/components/          feature components (auth/, chat/, dashboard/, layout/)
src/types/               TypeScript types mirroring backend schemas
tests/unit/              pure logic + hook tests, no network
tests/integration/       component tests with MSW-mocked network calls
entrypoint.sh            generates runtime env config, then starts the server
```

See [`CLAUDE.md`](./CLAUDE.md) for the full data-flow architecture, the
established patterns to follow for new code, and a list of hard rules
that exist because breaking them already caused real bugs — worth a read
before making non-trivial changes here.

## Getting started

**Prerequisites:** [Bun](https://bun.sh) 1.4+, a reachable backend API
(see [`src/backend/README.md`](../backend/README.md) or run the whole
stack via the [repo root README](../../README.md)).

```bash
cd src/frontend
bun install

# Configure environment (from the repo root)
cd ../..
cp .env.fe.example .env.fe
# edit .env.fe — NEXT_PUBLIC_API_URL should point at your backend

cd src/frontend
bun run dev
```

The app is now at `http://localhost:3000`.

**Or run it via Docker** instead of installing anything locally — see the
[repo root README](../../README.md#-quick-start).

## Environment variables

Copy `.env.fe.example` (at the repo root) to `.env.fe` and fill in the
values.

| Variable | Required | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API base URL, resolved at container **runtime** — see `src/lib/env.ts` and Critical Rule 1 in `CLAUDE.md` |
| `PORT` | No (default `3000`) | Port the server listens on |

If the API is on a different subdomain than the frontend, the backend also
needs `CORS_ORIGINS` and `COOKIE_DOMAIN` set — see the backend README's
[environment variables](../backend/README.md#environment-variables).

Changing `PORT` here only changes what the app listens to inside its
container — `docker-compose.yml`'s host-side port mapping is separate
and needs updating by hand to match (see `CLAUDE.md`'s Critical Rule 9).

## Testing

```bash
cd src/frontend
bun test                    # everything
bun run test:unit           # pure logic + hooks, no network
bun run test:integration    # components, MSW-mocked network calls
bun test --watch
```

No database, no Docker container, no running dev server required. See
`CLAUDE.md`'s "Testing" section for the test infrastructure's non-obvious
gotchas (preload ordering, the shared MSW server lifecycle, Radix
`Select` testing quirks) before touching `tests/setup.ts`,
`tests/dom.setup.ts`, or `tests/msw.setup.ts`.

## Building for production

```bash
bun run build
bun run start
```

`next build` type-checks everything under `src/` but not `tests/`
(excluded in `tsconfig.json` — test files use Bun/jest-dom-specific
globals the Next.js build environment doesn't know about; `tests/tsconfig.json`
covers them separately for editor support).

## Docker

```bash
docker build -t ailearning-frontend -f Dockerfile .
```

- 3-stage build (`oven/bun:1.4.2-alpine`, pinned exact patch) —
  `bun install --frozen-lockfile`, `bun run build`, then a minimal runner
  stage.
- No build-time `PORT`/`HOSTNAME` — both are resolved at container
  runtime by `entrypoint.sh` (see `CLAUDE.md` Critical Rule 3).
- `entrypoint.sh` writes `public/env-config.js` from the container's
  runtime environment before starting the server, so the same image
  works unmodified across environments — see Critical Rule 1.
- Runs as a non-root user (`nextjs`).

## Pages

All routes are under `src/app/`. `(auth)` and `(dashboard)` are Next.js
route groups — they don't appear in the URL.

| Route | File | Access | What it does |
|---|---|---|---|
| `/login`, `/register` | `(auth)/*/page.tsx` | Public | `RegisterForm` lets any visitor pick `role: teacher` — see `CLAUDE.md`'s "Known, deliberately deferred gaps" |
| `/dashboard` | `(dashboard)/dashboard/page.tsx` | Protected | Role-specific landing view — `StudentDashboard` or `TeacherDashboard` |
| `/courses`, `/courses/[id]`, `/courses/create` | `(dashboard)/courses/**` | Protected | Browse/create/manage courses |
| `/classes`, `/classes/[id]`, `/classes/create` | `(dashboard)/classes/**` | Protected | Classes within a course; students enroll from here |
| `/tasks`, `/tasks/[id]`, `/tasks/create` | `(dashboard)/tasks/**` | Protected | Tasks a teacher assigns; the thing a chat session is scoped to |
| `/chat/sessions`, `/chat/[sessionId]` | `(dashboard)/chat/**` | Protected | The student-facing tutoring chat — see `useChat` in [Architecture & data flow](#architecture--data-flow) |
| `/analytics` | `(dashboard)/analytics/page.tsx` | Protected, teacher-facing | Course → class → task drill-down, a 9-signal behavior-mix chart per group, and a per-student table ranked by prompt count |
| `/analytics/student/[studentId]` | `(dashboard)/analytics/student/[studentId]/page.tsx` | Protected, teacher-facing | One student's own classification summary, plus their chat sessions — expandable into the full conversation or a "prompts only" view |
| `/enrollments/join` | `(dashboard)/enrollments/join/page.tsx` | Protected | Student joins a class (by code/link) |

See the [repo root README](../../README.md#-the-teacher-dashboard) for
what the analytics pages look like from a teacher's point of view, not
just which files they live in.

## Troubleshooting

**Frontend can't reach the API / calls go to `undefined`** — check
`NEXT_PUBLIC_API_URL` in `.env.fe`, and confirm you're not reading
`process.env.NEXT_PUBLIC_API_URL` directly anywhere client-side (see
[Architecture & data flow](#architecture--data-flow)). Changing the value
and restarting the container is enough — no rebuild needed, since it's
resolved at runtime via `public/env-config.js`.

**A protected page's shell renders for a logged-out visitor** — the route
guard didn't load. Confirm the file is exactly `src/proxy.ts` (sibling of
`src/app`, not `src/frontend/middleware.ts` or any other location/name)
and exports a function named `proxy`. Verify live, not just by reading the
code: build the image, `curl` a protected path with no cookie, and confirm
a `307` to `/login`.

**Login succeeds but you land back on `/login`** — `proxy.ts` never saw the
`access_token` cookie. With the API on a different subdomain, set
`COOKIE_DOMAIN` (e.g. `.example.com`) in the backend's `.env.be`; the
cookie is otherwise host-only to the API host. Check the login response
in dev tools for a `Set-Cookie` header with the right `Domain`.

**Stuck in a redirect loop to `/login`** — check `src/lib/api.ts`'s 401
response interceptor; it's guarded against redirect loops but a change
here is exactly the kind of thing that can silently reintroduce one.

**A component test fails with "found multiple elements" on a Radix
`Select` value** — query `getByRole("option", { name: "..." })`, not
`getByText(...)`. Radix renders the selected item's text twice (a hidden
measurement copy + the real option), and happy-dom doesn't compute layout
well enough for jest-dom's visibility filtering to exclude the hidden one.

**The full `bun test` suite fails with `ECONNREFUSED` but individual test
files pass** — don't add a per-file `beforeAll(() => server.listen())`
for the MSW server; it's a shared singleton whose lifecycle is registered
once, globally, in `tests/msw.setup.ts`. Always verify a test change
against the full suite, not just the file you touched — see `CLAUDE.md`'s
"Testing" section for the full story.

**A new page/component is missing labels/ARIA attributes at runtime even
though the JSX looks right** — in a `components/ui/form.tsx`-based form,
`FormControl` must wrap the actual input element directly, never a
wrapping `<div>`. If an input needs a sibling overlay (an icon button, a
suffix), put that wrapping `<div>` *outside* `FormControl`.

For anything not covered here, `CLAUDE.md`'s "Critical rules" section has
the full incident behind each of these — worth reading before assuming a
fix is safe.

## Claude Code project tooling

This directory has its own `.claude/`:

- **`CLAUDE.md`** — architecture, hard conventions, and known gaps.
- **`.claude/skills/`** — twelve skills, each invocable as `/<name>` or
  picked up automatically when relevant:
  - **`dev-server`** — start the frontend locally the correct way (env,
    reachability check against the backend, `bun run dev`).
  - **`check`** — comprehensive check: lint, production build, and the
    full test suite, with a consolidated pass/fail report. Run this
    before considering a change done.
  - **`test`** — run the Bun test suite, unit and/or integration.
  - **`docker-smoke-test`** — build the Docker image and exercise it end
    to end (healthcheck, runtime env injection, route guard, `HOSTNAME`
    binding) against real requests, not just a successful build.
  - **`new-page`** — scaffold a new protected page following this
    codebase's data-fetching and form conventions.
  - **`new-component`** — scaffold a new component, presentational or
    stateful, using the right shadcn/ui + form conventions.
  - **`new-hook`** — scaffold a new `src/hooks/` hook, thin query/mutation
    wrapper or stateful, following `useAuth`/`useChat`'s patterns.
  - **`new-service`** — scaffold a new `src/services/` file or method,
    following the thin-axios-wrapper convention every existing one uses.
  - **`modularize`** — find and extract reusable components/hooks/services
    out of pages that have grown large or duplicated, without changing
    behavior — verified against the test suite before and after.
  - **`security-check`** — review a diff against this frontend's specific
    security checklist (token/session handling, route protection, XSS
    surface, CSP, dependency hygiene).
  - **`enrich-unit-tests`** — audit and deepen `tests/unit/` coverage.
  - **`enrich-integration-tests`** — audit and deepen
    `tests/integration/` coverage: the full loading/success/error/empty
    state matrix per component, and MSW-mocked edge cases.

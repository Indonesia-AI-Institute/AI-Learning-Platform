# AI Learning Platform — Frontend

Next.js 16 (App Router) + React 19 frontend for the AI Learning Platform:
course/class/task views for teachers, session-based AI tutoring chat for
students, and prompt analytics dashboards. TanStack Query for
server-state, react-hook-form + zod for forms, shadcn/ui (Radix) for
components, JWT auth via an httpOnly cookie the frontend never touches
directly.

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

See [`CLAUDE.md`](./CLAUDE.md) for the data-flow architecture, the
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
[repo root README](../../README.md#getting-started).

## Environment variables

Copy `.env.fe.example` (at the repo root) to `.env.fe` and fill in the
values.

| Variable | Required | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API base URL, resolved at container **runtime** — see `src/lib/env.ts` and Critical Rule 1 in `CLAUDE.md` |
| `PORT` | No (default `3000`) | Port the server listens on |

The root `.env` (from `.env.example`) is a separate, optional file for
`docker compose`'s own port-mapping/orchestration config — see the repo
root README and `CLAUDE.md`'s Critical Rule 9.

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

| Route | File | Access |
|---|---|---|
| `/login`, `/register` | `(auth)/*/page.tsx` | Public |
| `/dashboard` | `(dashboard)/dashboard/page.tsx` | Protected — role-specific view (student/teacher) |
| `/courses`, `/courses/[id]`, `/courses/create` | `(dashboard)/courses/**` | Protected |
| `/classes`, `/classes/[id]`, `/classes/create` | `(dashboard)/classes/**` | Protected |
| `/tasks`, `/tasks/[id]`, `/tasks/create` | `(dashboard)/tasks/**` | Protected |
| `/chat/sessions`, `/chat/[sessionId]` | `(dashboard)/chat/**` | Protected — streaming chat |
| `/analytics`, `/analytics/student/[id]` | `(dashboard)/analytics/**` | Protected — teacher-facing |
| `/enrollments/join` | `(dashboard)/enrollments/join/page.tsx` | Protected — student joins a class |

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

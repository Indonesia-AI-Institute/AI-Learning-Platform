---
name: dev-server
description: Start the AI Learning Platform frontend locally for development — verifies/creates .env.fe, then runs `bun run dev` with hot reload. Use when asked to run, start, or serve the frontend outside Docker.
---

# Frontend dev server

Runs the Next.js frontend locally (not via Docker) with hot reload.

## Steps

1. **Confirm working directory context.** Commands below run from the
   repo root except where noted; the frontend project itself lives at
   `src/frontend/`.

2. **Ensure `.env.fe` exists** at the repo root. If missing, copy
   `.env.fe.example` to `.env.fe`. `NEXT_PUBLIC_API_URL` should point at
   wherever the backend is actually reachable (`http://localhost:8000/api/v1`
   for a locally-run backend). `PORT` is optional (defaults to 3000).

3. **Confirm the backend is reachable** at that URL if the user is about
   to exercise anything beyond static pages (login, chat, etc.) — check
   with a quick `curl -sf <url>/health` or equivalent rather than assuming.
   If it's not running, say so rather than silently starting the frontend
   anyway; login/data-fetching pages won't work without it.

4. **Install dependencies** (idempotent, safe to always run):
   ```bash
   cd src/frontend && bun install
   ```

5. **Start the dev server:**
   ```bash
   cd src/frontend && bun run dev
   ```
   Run this in the background (or foreground per the user's stated
   preference) — it's a long-running process, not a one-shot command.

6. **Report back**: the URL (`http://localhost:3000` by default, or
   whatever `PORT` was set to), and how to stop it (Ctrl+C, or note the
   background task if launched that way).

## If it fails to start

- `EADDRINUSE` → something else is already on that port. Ask whether to
  use a different `PORT` or stop the other process — don't silently kill
  an unrelated process.
- Pages that need auth/data show fetch errors → almost always means
  `NEXT_PUBLIC_API_URL` in `.env.fe` doesn't point at a reachable backend.
  Verify step 3 was actually checked.
- `bun: command not found` → Bun isn't installed. Install via
  `curl -fsSL https://bun.sh/install | bash`, matching this repo's
  pinned version if one is documented in `src/frontend/Dockerfile`
  (`corepack`/Bun base image tag).

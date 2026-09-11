---
name: full-stack-dev
description: Bring up the whole stack (Postgres + backend API + frontend) together via docker compose for local development or manual end-to-end testing. Use when asked to run, start, or spin up the full app, or when a change needs to be verified against the real frontend-to-backend integration rather than one side in isolation.
---

# Full-stack dev environment

Brings up all three services (`db`, `api`, `frontend`) from
`docker-compose.yml` (the dev file — builds images locally, bundles a
local Postgres) for local development or manual verification. For
working on just one side without Docker, use that project's own
`dev-server` skill instead.

## Steps

1. **Confirm a Docker daemon is reachable** (`docker info`). If not and
   the machine uses Colima, check `colima list` for an existing profile
   and start that one — don't invent a new profile name; ask the user
   which to use if none exists yet.

2. **Ensure `.env.be` and `.env.fe` exist** at the repo root. If either
   is missing, copy from its `.example` and fill in the required values —
   `SECRET_KEY` (≥32 random characters), `POSTGRES_USER`/`POSTGRES_PASSWORD`,
   and an LLM provider key (`OPENROUTER_API_KEY` is the easiest to get a
   free-tier key for) at minimum. Don't guess secret values — ask, or
   generate a random one for `SECRET_KEY`/`POSTGRES_PASSWORD` specifically
   since those don't need to be memorable.

3. **Bring the stack up:**
   ```bash
   docker compose up -d --build
   ```
   `--build` matters if source has changed since the images were last
   built — Compose won't rebuild automatically just because a source file
   changed.

4. **Wait for all three to report healthy**, not just "running":
   ```bash
   until [ "$(docker inspect -f '{{.State.Health.Status}}' ailearning-db)" = "healthy" ] && \
         [ "$(docker inspect -f '{{.State.Health.Status}}' ailearning-api)" = "healthy" ] && \
         [ "$(docker inspect -f '{{.State.Health.Status}}' ailearning-frontend)" = "healthy" ]; do
     sleep 2
   done
   ```

5. **Report the URLs**: API at `http://localhost:8000` (docs at `/docs`),
   frontend at `http://localhost:3000`. Changing either requires editing
   both `PORT` in `.env.be`/`.env.fe` *and* the matching `ports:` line in
   `docker-compose.yml` by hand — the two aren't linked automatically
   (see the root `CLAUDE.md`'s Critical Rule 1).

6. **Leave it running** unless asked to tear down — this is meant to
   support further interactive work (manual testing, iterating on a fix),
   not a one-shot smoke test. For an automated end-to-end verification
   pass instead (registration flow, route guard, then teardown), use
   `docker-smoke-test`.

## If a service won't go healthy

- **`db` unhealthy**: check `docker compose logs db` — usually a bad
  `POSTGRES_*` value in `.env.be`, or a leftover volume from a previous,
  differently-configured run (`docker compose down -v` to reset it, but
  confirm with the user first — this destroys the local database).
- **`api` unhealthy**: check `docker compose logs api` — a missing
  `SECRET_KEY`/`DATABASE_URL` in `.env.be` fails fast with a clear
  pydantic validation error; a migration failure shows in the same logs
  since `entrypoint.sh` runs migrations before starting uvicorn.
- **`frontend` unhealthy**: check `docker compose logs frontend` — this
  is rarer since the frontend has few runtime dependencies; if it's
  healthy but pages error, that's almost always `NEXT_PUBLIC_API_URL` in
  `.env.fe` not pointing at the api service correctly.

## Tearing down

```bash
docker compose down          # stop and remove containers, keep the db volume
docker compose down -v       # also delete the local database — confirm first
```

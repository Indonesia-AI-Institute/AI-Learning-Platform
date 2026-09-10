---
name: docker-smoke-test
description: Build the backend's Docker image and verify it end to end against a real, disposable Postgres container — migrations run, the app boots, auth (register/login/me/logout/blacklist) works, and the previously-open chat endpoint correctly requires auth. Use before merging or deploying a change that touches the Dockerfile, entrypoint.sh, auth, or the migration chain — a unit/integration test pass does not prove the container actually boots.
---

# Backend Docker smoke test

Live end-to-end verification that the actual built image works, not just
the source code in isolation. This is what would have caught, live, the
`bcrypt`/`passlib` incompatibility that broke registration and login
completely — that bug was invisible to static review and to a container
that merely built and imported cleanly; it only showed up when a real
password hash was actually computed.

## When to run this

- Changes to `src/backend/Dockerfile` or `src/backend/entrypoint.sh`
- Dependency version changes in `pyproject.toml`, especially anything
  touching `passlib`, `bcrypt`, `python-jose`, `sqlalchemy`, `asyncpg`, or
  `alembic`
- Changes to auth (`auth/security.py`, `api/deps.py`,
  `services/auth_service.py`) or to any migration
- Before a release / before merging a branch with backend infra changes

Not needed for a routine schema/route/service change that's already
covered by the integration test suite — reach for the `test` skill for
that; this one is specifically about proving the *container* works.

## Steps

1. **Get a Docker daemon reachable.** Check `docker info`; if using
   Colima, `colima list` and start whichever profile is already
   configured (don't invent a new one — ask the user if none exists).

2. **Build the image** from the repo root:
   ```bash
   docker build -f src/backend/Dockerfile -t ai-learning-backend:smoketest ./src/backend
   ```
   A failure here is itself the finding — report the build error, don't
   proceed.

3. **Start a disposable Postgres** on its own network:
   ```bash
   docker network create iaii-smoke
   docker run -d --rm --name pg-smoke --network iaii-smoke \
     -e POSTGRES_USER=smoke -e POSTGRES_PASSWORD=smoke -e POSTGRES_DB=smoke \
     postgres:15-alpine
   until docker exec pg-smoke pg_isready -U smoke -d smoke; do sleep 1; done
   ```

4. **Run the backend image** against it, with a valid (throwaway)
   `SECRET_KEY` and `CORS_ORIGINS` — both are required, the app won't
   boot without them:
   ```bash
   docker run -d --rm --name api-smoke --network iaii-smoke -p 18000:8000 \
     -e DATABASE_URL="postgresql+asyncpg://smoke:smoke@pg-smoke:5432/smoke" \
     -e SECRET_KEY="smoke-test-secret-key-at-least-32-characters" \
     -e CORS_ORIGINS='["http://localhost:3000"]' \
     ai-learning-backend:smoketest
   ```
   Check `docker logs api-smoke` for migrations completing and uvicorn
   starting. If migrations fail here, that's a real finding — don't
   retry with a different database hoping it goes away.

5. **Exercise the auth flow for real**, via curl against
   `http://localhost:18000/api/v1`:
   - `POST /auth/register` → expect `201` with an `access_token`
   - `GET /auth/me` with that token as `Authorization: Bearer` → expect
     `200` with the user, and confirm no `hashed_password`/`password`
     field leaks into the response
   - `POST /auth/logout` with that token → expect `200`
   - `GET /auth/me` again with the *same* token → expect `401` (proves
     the token blacklist actually rejects a revoked token, not just that
     logout returns 200)
   - `POST /chat/direct/generate` with **no** auth header → expect `401`
     (this endpoint used to have no auth check at all)

   Treat any deviation from these exact expectations as a real failure
   to report, not something to explain away.

6. **Clean up everything this skill created**, whether the run passed or
   failed:
   ```bash
   docker stop api-smoke pg-smoke
   docker network rm iaii-smoke
   docker rmi ai-learning-backend:smoketest
   ```
   Only stop a Colima/Docker daemon this skill itself started — leave
   pre-existing state alone.

7. **Report a clear pass/fail summary** — which of the checks in step 5
   passed, and the exact response (status + body) for anything that
   didn't match expectations.

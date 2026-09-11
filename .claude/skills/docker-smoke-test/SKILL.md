---
name: docker-smoke-test
description: Build all three images (db is prebuilt, api and frontend built locally) and bring the full stack up together via docker compose, verifying real cross-service integration — a live registration call through the frontend's actual API URL resolution, the route guard, and health checks — not just that each image builds. Use when asked to smoke-test the full stack, or to verify a deployment-related change actually works end to end before merging.
---

# Full-stack Docker smoke test

Each project has its own `docker-smoke-test` skill that verifies ONE
image in isolation (its own healthcheck, its own runtime env injection).
This one verifies the INTEGRATION — that the frontend and backend
containers can actually reach and authenticate against each other the
way a real deployment would, which neither project's own skill can catch
alone.

## Steps

1. **Confirm a Docker daemon is reachable** (`docker info`; on Colima,
   reuse an existing profile per `colima list` rather than starting a new
   one).

2. **Ensure `.env.be` and `.env.fe` exist** at the repo root (copy from
   `.example` and fill in required values if not — see `full-stack-dev`
   for what's required). These can be throwaway dev values for this
   smoke test specifically (a random `SECRET_KEY`, a placeholder LLM key
   if the test doesn't need real chat) — but say so if generating them,
   rather than silently fabricating credentials the user might mistake
   for real ones.

3. **Build and bring up the full stack:**
   ```bash
   docker compose up -d --build
   ```

4. **Wait for all three services to report healthy** (see
   `full-stack-dev` for the exact wait loop).

5. **Verify the backend directly:**
   ```bash
   curl -s http://localhost:8000/api/v1/health
   ```

6. **Verify the frontend's route guard** (this is `src/proxy.ts` — see
   `src/frontend/CLAUDE.md` Critical Rule 2 for why this specific check
   matters: this exact guard was once silently inert for a full session
   because the file lived at the wrong path, and only an end-to-end check
   like this one would have caught it, not a unit test or a successful
   build):
   ```bash
   curl -sI http://localhost:3000/dashboard | grep -E "^HTTP|location"
   # must be a 307 redirect to /login
   ```

7. **Verify real cross-service integration with a live registration
   call** through the backend directly (proves the db + api are wired
   correctly end to end — migrations ran, the schema is correct, auth
   works):
   ```bash
   curl -s -X POST http://localhost:8000/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"smoketest@example.com","password":"SmokeTest123!","full_name":"Smoke Test","role":"student"}' \
     -w "\nHTTP %{http_code}\n"
   # expect 201 and an access_token in the body
   ```

8. **Verify the frontend's runtime env injection points at the right
   API** (proves the frontend container would actually be able to reach
   this exact backend in a real deployment, not just that both containers
   independently work):
   ```bash
   curl -s http://localhost:3000/env-config.js
   # NEXT_PUBLIC_API_URL here must match what .env.fe set
   ```

9. **Report results plainly** — which checks passed, and the exact output
   of any that didn't.

10. **Clean up:**
    ```bash
    docker compose down
    ```
    Ask before adding `-v` — that deletes the local database volume, which
    may hold data the user cares about from earlier manual testing.

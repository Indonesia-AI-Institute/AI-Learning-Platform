---
name: docker-smoke-test
description: Build the AI Learning Platform frontend's Docker image and exercise it end to end — healthcheck, runtime env injection, route guard behavior, dynamic PORT/HOSTNAME. Use when asked to verify the Dockerfile, entrypoint.sh, or a deployment-related change actually works, not just that it builds.
---

# Frontend Docker smoke test

A successful `docker build` proves the image compiles — it proves nothing
about whether the container actually starts, binds correctly, or serves
the right thing. This skill verifies the parts that have broken silently
before: runtime env injection, the `HOSTNAME` binding fix, and the
`src/proxy.ts` route guard.

## Steps

1. **Confirm a Docker daemon is reachable** (`docker info`). If not and
   the machine uses Colima, check `colima list` for an existing profile
   and start that one — don't invent a new profile name; ask the user
   which to use if none exists yet.

2. **Build the image:**
   ```bash
   docker build -t ailearning-frontend-smoketest -f src/frontend/Dockerfile src/frontend
   ```
   If it fails with a `docker.io` DNS/registry timeout, retry once — this
   has been a transient Colima-networking issue before, not a real build
   problem.

3. **Run it with a non-default PORT** (proves rule 3 in `CLAUDE.md` — no
   build-time default, `HOSTNAME` force-set):
   ```bash
   docker run -d --name fe-smoketest -p 9090:9090 \
     -e PORT=9090 \
     -e NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 \
     ailearning-frontend-smoketest
   ```

4. **Wait for healthy, not just "running":**
   ```bash
   until [ "$(docker inspect -f '{{.State.Health.Status}}' fe-smoketest)" = "healthy" ]; do sleep 1; done
   ```

5. **Verify runtime env injection** (proves Critical Rule 1 — the value
   isn't baked in at build time):
   ```bash
   curl -s http://localhost:9090/env-config.js
   # must show the NEXT_PUBLIC_API_URL passed via -e above, not a build-time value
   ```

6. **Verify the route guard** (proves Critical Rule 2 — this is the rule
   that silently didn't work for an entire session because the file was
   in the wrong location; this exact check is what would have caught it):
   ```bash
   curl -sI http://localhost:9090/dashboard | grep -E "^HTTP|location"
   # must be a 307 redirect to /login, not a 200
   curl -s -o /dev/null -w "%{http_code}\n" http://localhost:9090/login
   # must be 200 (public path)
   ```

7. **Verify `HOSTNAME` is actually `0.0.0.0` inside the container**, not
   the auto-populated container ID:
   ```bash
   docker exec fe-smoketest sh -c "cat /proc/1/environ | tr '\0' '\n' | grep HOSTNAME"
   ```

8. **Report results plainly** — which checks passed, and the exact output
   of any that didn't. A healthy container that fails the route-guard
   check is a real regression, not a pass with an asterisk.

9. **Clean up** what this skill started:
   ```bash
   docker rm -f fe-smoketest
   docker rmi ailearning-frontend-smoketest
   ```
   If a Colima VM was already running before this skill touched anything,
   leave it running — only stop what this skill itself started.

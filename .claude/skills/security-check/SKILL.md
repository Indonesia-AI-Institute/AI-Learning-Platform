---
name: security-check
description: Review the integration surface between backend and frontend for security issues neither project's own security-check would catch alone — CORS/cookie/CSP consistency with the actual deployment topology, secret leakage across the env-file boundary, and network exposure in the compose files. Use when asked to review cross-cutting or deployment-level security, or before a production deployment change.
---

# Full-stack security check

Each project's own `security-check` skill (`src/backend/.claude/skills/`,
`src/frontend/.claude/skills/`) reviews that project in isolation. This
one is specifically for the seam between them — things that are only
wrong when you look at both sides together.

## Checklist

**CORS / cookie / CSP consistency**
- [ ] `CORS_ORIGINS` in `.env.be` actually lists the frontend's real
      deployed origin(s) — not just `localhost`, if this is being
      checked ahead of a production deployment. A mismatch here doesn't
      fail loudly; browsers just silently block the response, which
      looks like "the API is broken" to whoever reports it.
- [ ] The backend's cookie `samesite`/`secure` attributes
      (`src/backend/api/v1/auth_routes.py`) are compatible with the
      actual deployment topology. `SameSite=Lax` works fine for same-site
      or same-registrable-domain deployments; if frontend and backend
      ever end up on genuinely different domains (not subdomains of the
      same site), cookies stop being sent on cross-origin `fetch` calls
      entirely, silently breaking auth — this is a real constraint to
      flag before such a deployment, not fix reactively after.
- [ ] The frontend's CSP `connect-src` (`next.config.ts`) is currently a
      wildcard (`*`) specifically because `NEXT_PUBLIC_API_URL` is
      resolved at container runtime, not build time — see
      `src/frontend/CLAUDE.md`'s known gaps. If that ever changes (e.g.
      the API origin becomes knowable at build time), this is the
      directive to tighten; don't tighten it without also confirming the
      runtime-resolution mechanism still works.

**Secret leakage across the env-file boundary**
- [ ] No value from `.env.be` (`SECRET_KEY`, `POSTGRES_PASSWORD`, any LLM
      provider API key) ever appears as a `NEXT_PUBLIC_*` variable in
      `.env.fe` or in `docker-compose*.yml`'s frontend `environment:`
      block. `NEXT_PUBLIC_*` is inlined into the client-side JS bundle —
      anything with that prefix should be treated as visible to every
      visitor, unconditionally.
- [ ] `docker-compose*.yml`'s frontend service doesn't have build-time
      `args:` that could bake in anything backend-side — check both the
      dev and prod compose files, since they're allowed to diverge (root
      `CLAUDE.md` Critical Rule 2) and a fix to one doesn't imply the
      other was checked.

**Network exposure**
- [ ] `docker-compose.prod.yml` doesn't expose Postgres (`db`) to the
      host — production is designed around an external/managed Postgres
      with no bundled `db` service at all; if one gets added back for
      convenience, it must not get a host `ports:` mapping.
- [ ] The API's host port mapping in `docker-compose.prod.yml` (currently
      none — see root `CLAUDE.md` Critical Rule 2) hasn't been added back
      without a deliberate decision that it should be internet-reachable
      directly, as opposed to sitting behind whatever the actual
      production topology puts in front of it.

**Route protection vs. actual auth requirements**
- [ ] Every backend endpoint that requires auth has a frontend page that
      sits behind `src/proxy.ts`'s guard (or is deliberately public data
      shown via a public page) — a mismatch here isn't usually an actual
      vulnerability (the backend is the real boundary either way, per
      `src/frontend/CLAUDE.md`'s known gaps), but a protected page that
      *isn't* behind the frontend guard produces a confusing UX where the
      shell renders before the 401 kicks the user out, worth catching
      anyway.

## Reporting

For each finding: which file(s), what's inconsistent between the two
sides, and the concrete failure mode (not just "this could be an issue")
— matching the standard each project's own `security-check` skill uses.
If a section has nothing to report, say so explicitly rather than
omitting it.

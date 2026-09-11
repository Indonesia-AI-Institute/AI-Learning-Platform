# AI Learning Platform

A full-stack AI-tutoring platform: teachers manage courses/classes/tasks,
students chat with an LLM through session-based chat tied to a task, and
a background classifier gives teachers prompt analytics with zero added
latency for the student.

This file is project memory for whoever (human or Claude) works anywhere
in this repo. It covers the **whole monorepo** — orchestration, deployment,
and the things that span both halves of the stack. The backend and
frontend are each independent Claude Code projects with their own,
more detailed memory:

- **[`src/backend/CLAUDE.md`](src/backend/CLAUDE.md)** — FastAPI
  architecture, request-flow, auth internals, the backend's own critical
  rules.
- **[`src/frontend/CLAUDE.md`](src/frontend/CLAUDE.md)** — Next.js
  architecture, the route guard, CSP, the frontend's own critical rules.

Read the relevant one before making non-trivial changes inside `src/backend/`
or `src/frontend/` — this file intentionally doesn't repeat their content.

## Repo layout

```
src/backend/    FastAPI + SQLAlchemy + PostgreSQL — see its own CLAUDE.md
src/frontend/   Next.js 16 + React 19 — see its own CLAUDE.md
docker-compose.yml        dev: builds both images locally, bundles a local db
docker-compose.prod.yml   prod: pulls prebuilt GHCR images, no bundled db
.env.be.example            backend runtime config (copy to .env.be)
.env.fe.example            frontend runtime config (copy to .env.fe)
.github/workflows/
  test-suite.yml         shared test jobs (unit and integration
                             variants per project), called by the three
                             below, takes a `scope: unit|integration`
                             input (not triggered directly)
  test.yml                  every push, any branch except main: unit
                             tests only, fast
  pr-validate.yml            every PR into main: unit + integration, then
                             (only if both pass) a real Docker build of
                             both images (no push to GHCR)
  release.yml                push to main: semantic-release (tags, pushes,
                             creates a GitHub Release) -> if a version was
                             cut, re-run unit + integration -> build+push
                             the final images. No CD — deployment is
                             manual, see the root README's "Docker: With
                             the Repository" section (docker compose -f
                             docker-compose.prod.yml pull/up).
```

Both `src/backend/` and `src/frontend/` are self-contained projects (own
lockfile, own Dockerfile, own test suite) that happen to live in one repo
and deploy together. Treat them as separately as their own CLAUDE.md files
do — don't reach into one from the other except through the HTTP API.

## Critical rules

**1. Only two env files — `.env.be` and `.env.fe`. Don't reintroduce a
third, root-level orchestration-only `.env`.** Both are loaded **inside
the containers** (`env_file:` in the compose files) and configure the
applications themselves; `PORT` in each controls what that app listens
to *inside* its container. A root `.env` file that fed `docker compose`
CLI's own `${VAR}` interpolation (to keep the host-side port mapping in
sync with `PORT` automatically) was built and then deliberately reverted
— this project settled on the simpler two-file split, accepting that
`docker-compose.yml`'s `ports:` mapping (`"8000:8000"`, `"3000:3000"`)
has to be changed by hand if a `PORT` value changes, rather than adding
a third file and an `environment:` override to automate it. If you find
yourself wanting `${SOME_VAR}` interpolation in a compose file again,
know that it can't read `.env.be`/`.env.fe` — Compose's own
substitution and `env_file:` are genuinely separate mechanisms — and
raise the tradeoff again rather than silently reintroducing the root
`.env` file.

**2. `docker-compose.yml` is dev, `docker-compose.prod.yml` is prod — don't
merge them, and don't assume one mirrors the other's tuning.** Dev builds
both images locally (`build:` context) and bundles a local `db` service;
prod pulls prebuilt `ghcr.io/.../*-api` / `*-frontend` images at
`${IMAGE_TAG:-latest}` and assumes an external/managed Postgres, with no
host port mapping for the API at all (not internet-exposed directly in
production). These two files are allowed to diverge on purpose, this
isn't drift to "fix."

**3. CI runs tests on every push and PR, but nothing currently blocks a
merge on a red check — and can't yet.** `test.yml` runs both projects'
*unit* suites on every push to a feature branch (fast, no Postgres);
`pr-validate.yml` runs *both* unit and integration on every PR into
`main`, then a real (unpushed) Docker build of both images if those pass;
`release.yml` re-runs *both unit and integration again* immediately
before building the final image — this duplicates the PR-time run, but
deliberately: since nothing enforces that PR check passing before a
merge is allowed (see below), this is the actual last gate before a real,
tagged image ships, not a redundant formality. Requiring those checks to
pass before merging needs GitHub branch
protection or repository rulesets, and **both are unavailable on this
repo right now** — it's private, and both features require GitHub
Pro/Team for a private repo (confirmed via `gh api .../branches/main/protection`
returning a 403 "Upgrade to GitHub Pro or make this repository public").
This isn't a config oversight to "just fix" — it needs a plan upgrade or
making the repo public, a real decision, before a required-status-check
rule can exist at all. Until then, a green PR check is real signal (a
change from before, when CI didn't run tests at all), but a human can
still click merge past a red one.

**4. Commit messages drive versioning.** `python-semantic-release`
(configured in the repo-root `pyproject.toml` — deliberately not
`src/backend/pyproject.toml`, since it versions the whole repo, not just
the backend) reads Angular/conventional-commit-style
messages (`feat|fix|perf|refactor|docs|style|test|chore|ci|build|revert: ...`)
on every push to `main` to decide the next version, tag it, and update
`CHANGELOG.md`. A non-conventional commit message doesn't fail anything,
it just doesn't contribute to the version bump — but sloppy messages
make the generated changelog useless, so follow the convention for
anything landing on `main`.

## Local development

See the root [`README.md`](README.md) for full setup instructions (Docker
and non-Docker paths, environment variables, LLM provider configuration,
troubleshooting). Short version:

```bash
cp .env.be.example .env.be && cp .env.fe.example .env.fe && cp .env.example .env
# fill in .env.be / .env.fe — SECRET_KEY, POSTGRES_*, an LLM provider key
docker compose up -d --build
```

For working on just one side without Docker, see that project's own
`CLAUDE.md`/`README.md` ("Running locally" / "Getting started").

## Testing

Each project's suite is independent and self-contained — see the `test`
skill in each project's `.claude/skills/` for the exact invocation
(`pytest` for the backend needs a real Postgres; `bun test` for the
frontend needs nothing but Bun). To check both at once before pushing,
use this repo's own `full-stack-check` skill — this is also exactly what
CI runs on every PR (see Critical Rule 3); a plain push to a branch only
runs the unit subset, faster but narrower. A clean local
`full-stack-check` run is a reliable predictor of the PR check passing,
not just a courtesy check.

## Known, deliberately deferred gaps

These span both halves of the stack and were evaluated, not missed —
don't "fix" them without a product decision:

- **No branch protection enforcing the CI test gate** (Critical Rule 3) —
  tests now run automatically on every push and PR, but merging past a
  failing check is still possible since no required-status-check rule is
  configured on `main`. Unlike most gaps in this list, this one **can't
  currently be closed by configuration alone**: both classic branch
  protection and repository rulesets require GitHub Pro/Team for a
  private repo, and this repo is private on a plan without either. Making
  the repo public or upgrading the org's plan is a real decision for
  whoever owns that call, not something to do unilaterally — once either
  happens, the required checks would be `pr-validate.yml`'s `test-unit`
  and `test-integration` (each surfacing a backend and a frontend check),
  plus `test-build-api` and `test-build-frontend`.
- **No automated deployment.** `.github/workflows/deploy.yml` (SSH to a
  production host, pull the latest images, restart via `deploy.sh`) was
  removed deliberately — CI now only builds and pushes images to GHCR on
  a version bump; nothing deploys them anywhere automatically. Pulling
  and restarting on a target host is a manual `docker compose -f
  docker-compose.prod.yml pull && up -d` (see the root README). If
  automated CD is wanted again, it needs a real decision on target host(s)
  and secrets, not just restoring the old workflow — the old script/SSH
  action are gone, not just disabled.
- **Teacher self-registration has no invite/approval gate.** `RegisterForm`
  on the frontend lets any visitor pick `role: teacher`, and the backend
  accepts it at face value (correctly ownership-scoped once created — see
  the backend `CLAUDE.md` Critical Rule 2 — but nothing gates *becoming*
  one). Documented identically on both sides since it's really one
  product decision, not two bugs.
- **No rate limiting anywhere** (login, register, chat streaming). Needs a
  library choice and real limit values, not a quick patch.

## Conventions

- Branch naming: `chore/<area>-<what>` for tidy-up/infra work (e.g.
  `chore/backend-tidyup`, `chore/frontend-tidyup`), otherwise
  `feat|fix/<short-description>` matching the commit-type prefix.
- PRs: a `## Summary` of what changed and why (not just what), and a
  `## Test plan` checklist of what was actually verified — lint/build/test
  results, and anything checked live (a real Docker container, a real
  curl call), not just "should work."
- Never commit `.env`, `.env.be`, or `.env.fe` — only the `.example`
  variants are tracked. If you ever see a real one staged, stop and
  check its contents before proceeding.

## Claude Code project tooling

- **This file** — repo-wide architecture, cross-cutting rules, and the
  versioning pipeline (there is no automated deployment — see "Known,
  deliberately deferred gaps").
- **`.claude/skills/`** — full-stack orchestration skills (bringing up
  the whole stack, checking both projects at once, understanding the
  release pipeline). Skills for scaffolding new code inside one project
  (a new endpoint, a new page, a new hook, etc.) live in that project's
  own `.claude/skills/` instead — see `src/backend/README.md` and
  `src/frontend/README.md` for those lists.

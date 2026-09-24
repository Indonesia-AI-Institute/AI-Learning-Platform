# CHANGELOG


## v1.3.0 (2026-09-24)

### Features

- **analytics**: Show student name instead of ID in teacher analytics
  ([`07d02e1`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/07d02e16a5bf54c20f959c43a43ecdb97723b77b))

The class/course/task classification endpoints now join users and return student_name alongside
  student_id. The teacher analytics table displays the name (falling back to the truncated ID),
  search matches name or ID, and the student detail page shows the name in its header.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>


## v1.2.2 (2026-09-20)

### Bug Fixes

- **auth**: Add COOKIE_DOMAIN so login works across subdomains
  ([`fbb667f`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/fbb667fdaccb17f91ea09b1ce8cf94280f43fe4f))

With the frontend and API on sibling subdomains, the access_token cookie had no Domain and was
  host-only to the API. The frontend's proxy.ts never saw it, so every login bounced back to /login.

Add an optional COOKIE_DOMAIN setting, applied to set_cookie on login/register and delete_cookie on
  logout. Empty keeps the previous host-only behaviour. Document it in the env template and READMEs,
  and add the other backend settings missing from the template (GEMINI_API_BASE, LOG_FILE,
  ENABLE_BANLIST_FILTER, BANNED_KEYWORDS).

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

### Continuous Integration

- Add a branded release-notes template
  ([`41abc78`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/41abc78354a79635ad708d0a5f2e8afc70247a65))

Give every GitHub Release a consistent, on-brand template instead of semantic-release's plain
  default:

- templates/.release_notes.md.j2 is the file PSR now renders each release's GitHub Release body from
  — a branded header/footer wrapped around the same unmodified Features/Bug Fixes/Breaking Changes
  grouping logic PSR ships by default. - templates/CHANGELOG.md.j2 and templates/.components/* are
  byte-for-byte copies of PSR's own default templates, required because semantic-release treats a
  custom template directory as all-or-nothing: once any other template exists there, CHANGELOG.md
  generation stops using PSR's built-in default too and needs its own file present, or CHANGELOG.md
  would simply stop updating on release. Verified this doesn't change CHANGELOG.md's output by
  diffing a real render before/after. - .github/release.yml adds GitHub's own native label-based
  release-notes categorization, for the "Generate release notes" button/`--generate-notes` path
  outside the automated pipeline.

Verified end-to-end in an isolated git worktree by simulating a real version bump through the exact
  `semantic-release version` command release.yml runs, with the pinned CI version (9.21.2) —
  confirmed the custom template renders correctly on that code path, not just via the standalone
  `changelog` command.

Documents the all-or-nothing template-directory behavior in CLAUDE.md so a future stray .j2 file
  added to templates/ doesn't silently break CHANGELOG.md generation, and fixes two small
  pre-existing doc bugs found while editing nearby text: a stale README anchor reference, and a
  leftover `cp .env.example .env` command referencing a third env file Critical Rule 1 says
  shouldn't exist.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

### Documentation

- Enrich backend and frontend project READMEs
  ([`dac4389`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/dac43896072a7c37edfbc675eff180a00a371aa0))

Both were accurate but terse — a project layout tree plus a handful of short reference sections.
  Expand them into comprehensive references for someone working in that project on its own:

Backend: an architecture diagram (request-flow layers, plus the chat side-path through agents/llm),
  a new section explaining the DirectTutor/ SocraticTutor agents and the exact nine
  prompt-classifier signals (with the asyncio.gather/create_task mechanism that gives zero added
  latency), a full LLM provider table, every Settings field with its default (cross-checked against
  core/config.py — including two things that look env-configurable but aren't), a complete
  per-resource API route table (verified against the actual route/function definitions), a Docker
  section, and a troubleshooting section drawn from CLAUDE.md's critical rules.

Frontend: a data-flow diagram (page -> hook -> service -> axios -> backend), an explanation of the
  route guard and runtime API URL resolution (why the same Docker image works unmodified across
  environments), how useChat's streaming bypasses the service layer, a richer Pages table with what
  each route actually does, and a troubleshooting section for the most likely real gotchas.

Also fixed two dangling cross-file links found while verifying every anchor in all three READMEs by
  script: both files still pointed at the root README's old "#getting-started" anchor, which the
  root README rewrite renamed to "Quick Start".

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

- Rewrite root README as a marketing front page
  ([`612f5dc`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/612f5dc29daeb903919c26ec58ae6fe003a768fe))

The old README was a technical reference (env var tables, migration commands, troubleshooting)
  duplicated across the repo root and each project's own README. Rewrite it as the project's front
  door instead: a pitch that leads with the actual problem this platform solves (giving teachers
  visibility into how students prompt an AI, not just whether they used one), a features list, a
  two-audience "How It Works" walkthrough with a diagram, a dedicated Teacher Dashboard section, and
  a separate "Under the Hood" section for the technical flow. Detailed setup/reference content now
  lives only in CLAUDE.md and the backend/frontend READMEs, linked from here instead of duplicated.

Quick Start keeps both Docker paths (pull prebuilt images vs. build from source) the root README
  already had, simplified to match the new tone.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>


## v1.2.1 (2026-09-11)

### Refactoring

- **ci**: Rename test-suite-* files, add image refs to GitHub Release notes
  ([`1fb13c6`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/1fb13c649ee8e64eb54965dcfab3f4dff691bb89))

Renames test-suite-unit.yml -> test-unit.yml and test-suite-integration.yml -> test-integration.yml
  (git mv, history preserved) for brevity, updating every reference across the workflow files,
  CLAUDE.md, and the release skill.

Adds a new update-release-notes job to release.yml, running only after both build-api and
  build-frontend push successfully: appends a "## Images" section with the exact ghcr.io
  image:version references to the GitHub Release body semantic-release already created. The release
  exists before the images do (PSR creates it, then the build jobs run), so this is a follow-up `gh
  release edit` rather than part of the original creation - it preserves PSR's changelog-derived
  notes and appends to them, not replaces them.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

- **ci**: Split test-suite.yml into unit/integration files, no more skipped jobs
  ([`5b17cc9`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/5b17cc9f3216998ed70108a5af06d5570eb30b5d))

test-suite.yml's scope input meant every call showed 2 of its 4 jobs as permanently skipped in the
  checks UI (whichever scope wasn't requested, gated via `if: inputs.scope == '...'`) — noisy, and
  not actually avoidable while all 4 job definitions lived in one reusable workflow.

Splits it into test-suite-unit.yml (backend+frontend unit jobs) and test-suite-integration.yml
  (backend+frontend integration jobs, the Postgres service container). Each caller (test.yml,
  pr-validate.yml, release.yml) now calls the specific file(s) it needs directly, with no scope
  input and no `if:` gating — every job a caller declares actually runs, so nothing shows as
  skipped.

Updates CLAUDE.md and the release skill to match.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>


## v1.2.0 (2026-09-11)

### Bug Fixes

- **frontend**: Reset the 401 redirect guard's module singleton between test files
  ([`98b6ba6`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/98b6ba640d12a45e277102025fbeafac6f987bf7))

pr-validate.yml's new full-suite test run (this branch's own CI change) immediately caught a real,
  pre-existing bug: src/lib/api.ts's isRedirecting flag is module-private state that's never reset,
  which is fine in production (a real redirect ends the page's JS context) but leaks across every
  test file in the same `bun test` process. tests/unit/api.test.ts's "redirects to /login on a 401
  when not already there" test only passed before because CI never ran the frontend suite at all,
  and locally it happened to run before any other file (useAuth/useCurrentUser/LoginForm's
  integration tests all trigger real 401s through the same shared api instance too) poisoned the
  flag first.

Adds a test-only __resetRedirectGuardForTests() export, called once in a beforeAll for api.test.ts's
  "api 401 redirect guard" describe block — this makes that block's own intentional internal
  test-ordering (documented in its existing comment) immune to whatever ran in other files before
  it, without touching the block's own sequencing.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

### Chores

- Remove automated deploy workflow and deploy.sh
  ([`d08e10e`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/d08e10ef2e3f76413201deaf75199c269367c4bc))

There is no production host wired up for the SSH-based CD step
  (PROD_SSH_HOST/PROD_SSH_USER/PROD_SSH_KEY/PROD_DEPLOY_PATH/CR_PAT secrets), so deploy.yml was dead
  automation - it would only ever run manually or never fire meaningfully. deploy.sh has no other
  caller, so it goes with it. Deployment is now documented as the manual `docker compose -f
  docker-compose.prod.yml pull && up -d` path that already existed in the README, rather than a
  half-wired automated one.

Updates CLAUDE.md (drops Critical Rule 3 on deploy.sh's location, renumbers the remaining rules,
  documents the removal under "Known, deliberately deferred gaps"), README.md, and the release skill
  to match - container-build.yml now only builds and pushes images to GHCR, nothing deploys them
  further.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

### Features

- **ci**: Split CI into test/PR-validate/release workflows, move release config to repo root
  ([`4e805f1`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/4e805f184b344d74d4063cc4d5d1efa3030e103f))

Replaces the single container-build.yml with four workflow files, each with one job:
  reusable-test.yml (shared test-backend/test-frontend jobs, called by the others, never triggered
  directly), test.yml (every push, any branch: tests only, fast feedback), pr-validate.yml (every PR
  into main: tests + a build-only Docker validation, no push, in parallel), and

release.yml (push to main: semantic-release -> if a version was cut, re-run the full test suite one
  more time against that exact commit -> only if that passes, build and push the final versioned
  images to GHCR). Previously nothing in CI ran pytest/bun test at all.

Moves python-semantic-release's [tool.semantic_release] config out of src/backend/pyproject.toml
  into a new repo-root pyproject.toml (no [project]/[build-system] table — it isn't a Python
  project, just a place for platform-level tool config that versions the whole repo, not just the
  backend). Also drops the two stray python-semantic-release entries from the backend's own
  dependency lists — it's a CI-installed tool (pip install python-semantic-release==9.* in
  release.yml), never a backend runtime or dev dependency.

Updates CLAUDE.md (repo layout, Critical Rule 3 no longer claims there's no CI test gate — it now
  documents that tests run but nothing enforces them via branch protection yet, Critical Rule 4's
  config path), backend CLAUDE.md, README.md, and the release skill to match.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

- **ci**: Split test scope into unit/full, gate PR build on tests passing
  ([`b5ce9a0`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/b5ce9a039da9652e6053cda4e32d62987aa68476))

Revises the CI split from the previous commit per review:

- reusable-test.yml now takes a `scope: unit|full` input. Branch pushes (test.yml) use scope=unit
  (fast, no Postgres, no integration suite — genuinely separate jobs, not just a narrower pytest
  path, since a service container can't be made conditional). PRs (pr-validate.yml) and the
  post-release check (release.yml) use scope=full (unit + integration). - pr-validate.yml's
  build-api/build-frontend now `needs: [test]` instead of running in parallel with it — no point
  spending build minutes validating a Dockerfile change whose tests already fail. - Confirmed (via
  `gh api .../branches/main/protection`, 403) that this repo can't yet get a required-status-check
  rule regardless of workflow config — both classic branch protection and rulesets need GitHub
  Pro/Team for a private repo, and this repo is private on a plan without either. Documented as a
  real, unresolved gap in CLAUDE.md rather than left implicit.

Updates CLAUDE.md, README.md, and the release skill to match.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

### Refactoring

- **ci**: True unit/integration split, fix GitHub Release creation, tidy workflows
  ([`4503943`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/450394356719cc957697c0e764e8954ba69f93a6))

Three changes on top of the previous CI-revamp commit:

- Splits reusable-test.yml's scope from unit/full into unit/integration (no combined scope):
  test.yml runs unit only on feature-branch pushes; pr-validate.yml calls both scopes separately on
  every PR, gating its Docker build on both passing; release.yml re-runs both scopes again
  post-release, gating the final image build on both — deliberately duplicating pr-validate.yml's
  checks, since nothing currently enforces those passing before a merge (no branch protection on
  this repo's GitHub plan), making this the real last gate before an image ships. - Fixes a real,
  separate bug: release.yml passed --no-vcs-release to `semantic-release version`, which suppresses
  GitHub Release creation — confirmed via `gh release list` returning empty despite 5 existing
  version tags. Removed the flag; `version` now tags, pushes, and creates the GitHub Release in one
  step. - Renames reusable-test.yml to test-suite.yml (git mv, history preserved) and trims comments
  across all four workflow files down to load-bearing "why" context, cutting restated/redundant
  explanation. - Renames pr-validate.yml's build-api/build-frontend jobs to
  test-build-api/test-build-frontend, dropping the "(validation only)"/ "(no push)" labels from job
  and step names.

Updates CLAUDE.md, README.md, and the release skill throughout to match.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>


## v1.1.0 (2026-09-11)

### Chores

- **frontend**: Make PORT/HOSTNAME runtime-only, fix dead build-arg
  ([`c3cba1b`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/c3cba1bb40e8e196a92d59b8614ed045481f73ae))

- Remove EXPOSE and the build-time ENV PORT=3000 default from the Dockerfile — PORT is now read at
  container start (entrypoint.sh, ${PORT:-3000}), not baked into the image. - HOSTNAME is force-set
  to 0.0.0.0 in entrypoint.sh rather than left as a "${HOSTNAME:-...}" fallback: Docker/Linux
  auto-populates HOSTNAME with the container ID before the entrypoint ever runs, so a fallback there
  never triggers. Verified live — this was actually binding the server to the container's bridge IP
  instead of all interfaces, making it unreachable from its own localhost (breaking the healthcheck
  below until fixed). - Add a HEALTHCHECK (curl added to the alpine runner stage). Verified via live
  build/boot on both the default port and an overridden one. - Remove docker-compose.yml's frontend
  build `args: NEXT_PUBLIC_API_URL` — the Dockerfile never declared a matching ARG, so it was
  silently inert; the `environment:` block (read by entrypoint.sh at runtime) is what actually
  works. - Fix a stale .dockerignore reference to the now-nonexistent .env.example. - Document PORT
  (optional) and the HOSTNAME non-option in .env.fe.example.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

- **frontend**: Migrate to Bun, fix runtime env leak, harden auth and CSP
  ([`3f2f43d`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/3f2f43de817b679e065513cb39da82d62f126d48))

- Switch package manager/runtime from pnpm to Bun end-to-end (Dockerfile, entrypoint.sh, lockfile,
  docs); bump dependencies within current majors - Fix useChat.ts reading NEXT_PUBLIC_API_URL
  directly, which Next.js inlines at build time and broke chat streaming in prod containers where
  it's intentionally not set at build time; route through getApiUrl() instead, which resolves it at
  container runtime - Remove dead Zustand auth store (never wired to any auth state) - Fix route
  protection: the existing middleware.ts lived outside src/, so Next.js never loaded it and
  unauthenticated visitors were never redirected; replace with src/proxy.ts (Next 16 renamed the
  convention), a presence-only cookie check backed by the backend's own auth as the real
  authorization boundary - Add CSP and other security headers (X-Frame-Options, nosniff,
  Referrer-Policy, Permissions-Policy) in next.config.ts - Make PORT dynamic end-to-end via
  docker-compose, threading a root .env's API_PORT/FRONTEND_PORT into both the container env and the
  host port mapping so they can't drift out of sync - Drop the dead rewrites() proxy config and
  stale msw trustedDependencies entry; trim excess comments across src/

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

### Features

- Add Claude Code skills for full-stack/backend/frontend workflows, backend ruff lint tooling
  ([`3c16132`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/3c161325b2b955c46cd3f17ac8b3e432c2c47b86))

Adds 4 new root-level orchestration skills (new-feature, open-pr, docs-sync-check, security-check)
  and 3 new backend skills (check, new-model, new-config-var), rounding out the three-tier Claude
  Code skill structure (root/backend/frontend) with the workflows this project's history shows are
  most needed — scaffolding a new model, catching declared-but-unread config toggles, and the
  commit/push/PR sequence already used twice manually.

Also introduces ruff as the backend's first static analysis tool (previously none existed). Rule set
  starts deliberately narrow (E/F/I/B) to surface correctness bugs without drowning in pre-existing
  style drift; fixes applied: - FastAPI's Depends(...)/RoleGuard(...) default-arg pattern configured
  as an immutable call so bugbear's B008 stops false-positiving on every route - dead `start_time`
  assignments (and now-unused `import time`) removed from both LLM provider files - two SQLAlchemy
  `== False` comparisons in user_repository.py annotated `# noqa: E712` (operator overload building
  a SQL expression, not a Python bool check — rewriting to `is not` would break the query) -
  alembic/env.py's deliberate `from backend.models import *` exempted from F403 - B904 (missing
  exception chaining, 74 pre-existing instances) deliberately left as a tracked ignore rather than
  mass-edited blind; `ruff format`'s 112-file reformat also deliberately not applied here, out of
  scope for this change

Full backend suite verified green (222/222) after these changes.

### Testing

- **frontend**: Add unit/integration test suite, Claude Code tooling, fix lint debt
  ([`4d2daea`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/4d2daeac7d2fe10441d379f644486be4ffadfe4f))

- Add a Bun test suite (unit/ + integration/, 109 tests) covering hooks, lib/proxy.ts, and the
  auth/chat/dashboard components, using MSW to mock the network boundary instead of mocking service
  modules - Add CLAUDE.md, README updates, and 12 Claude Code skills (dev-server, check, test,
  docker-smoke-test, new-page/component/hook/service, modularize, security-check,
  enrich-unit/integration-tests) - Fix a real accessibility bug found while testing LoginForm:
  FormControl wrapped a layout div instead of the input directly, breaking the password field's
  label association - Eliminate ~15 `any`-typed axios error handlers across the app into one typed
  helper (src/lib/errors.ts); type the remaining any usages in the analytics pages and useChat.ts -
  Fix set-state-in-effect errors in the course/class/task edit pages by initializing form state from
  the loaded record via lazy useState instead of syncing it in through a useEffect - Remove dead
  code found along the way (unused vars/imports, a duplicated formatDuration and PROMPT_TYPES table)

Lint: 0 errors (was 26). Build and full test suite verified green.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>


## v1.0.5 (2026-09-10)

### Refactoring

- **backend**: Restructure into src/backend, tidy Docker/deployment, cleanup
  ([`042ae05`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/042ae058e3581935a93b6bfbcbf240f1bc40276c))

- Move alembic/, alembic.ini, Dockerfile, .dockerignore, pyproject.toml, uv.lock into src/backend/
  so the backend is a self-contained uv project, matching the src/frontend/ layout. - Switch the
  backend Docker build from pip + requirements.txt to uv sync, fixing runtime deps (alembic,
  sqlalchemy, asyncpg, bcrypt, cryptography, python-multipart, email-validator) that were previously
  only covered by a stale, corrupted requirements.txt. - Rename all `src.backend.*` imports to
  `backend.*`; the Docker image now copies straight to /app/backend with no redundant src/ layer. -
  Add src/backend/entrypoint.sh wrapping migrations + uvicorn startup; simplify both docker-compose
  files accordingly. - Wire HOST/PORT fully to runtime with no build-time default (drop EXPOSE,
  which can't take a runtime value); add a real HEALTHCHECK against the existing /api/v1/health/live
  endpoint. - Split .env.example into .env.be.example / .env.fe.example. - Add
  docker-compose.prod.yml (registry-only) and restore docker-compose.yml as the local-build/dev
  file, matching README's existing documented convention. - Fix IMAGE_TAG never being applied in
  docker-compose.prod.yml (deploy.sh exported it but nothing read it); remove the alembic
  bind-mounts from prod compose (they overrode the image's baked-in migrations and broke the
  no-clone deploy path documented in README). - Remove excessive comments and confirmed-dead code
  across src/backend/ (core/constants.py, agents/registry/agent_factory.py, several unused
  repository methods and helpers), verified via repo-wide grep before removal.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>


## v1.0.4 (2026-08-24)

### Refactoring

- Add runtime env config for frontend
  ([`cc9b8ec`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/cc9b8ec71868f530c6dd5167ea3d6387c384ef4a))


## v1.0.3 (2026-06-24)

### Bug Fixes

- **workflow**: Python semantic release
  ([`d631fa6`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/d631fa640830ce06af0e389bcde4a0be2cb89e12))

### Chores

- Rename dockerfile
  ([`b5e65ce`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/b5e65cedb2a03b2a96f3c6d078c85992424c518a))


## v1.0.2 (2026-06-23)

### Bug Fixes

- Active session issue and minor bug
  ([`4d03604`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/4d0360439584f05e34711f73fc02f6434063c1bc))


## v1.0.1 (2026-06-22)

### Bug Fixes

- Change image docker tag to latest
  ([`9f74da5`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/9f74da563b791ad9cc7af3fd4bc8ea5b1370476d))

- Resolve active user session handling and update readme documentation
  ([`99e5242`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/99e5242f26874bb2641f18170c9135543d3865c2))

### Chores

- Test workflow
  ([`d9dc5d0`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/d9dc5d0faa16a00763a4169ced2bd0e9d200213f))

- Test workflow
  ([`5c6101c`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/5c6101cb8341f639ee09fd0f8b1895672ddad1cb))

- Update README.md for better documentation
  ([`976e04b`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/976e04baaf92324b74fa01b137229193aed5327e))


## v1.0.0 (2026-06-19)

### Bug Fixes

- Build frontend image workflow jobs
  ([`1270313`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/127031369e552ecd328e3b76eb3c56857cf745cc))

- Cant visualialize classificaion prompt analytics
  ([`57a65cf`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/57a65cfa29a5cba9cb8f38bedbcc826c522b95eb))

- Change tabl analytics layout and add code to edit task for teacher role
  ([`ad85593`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/ad85593f991d80f01969808b7357fc8773e47b99))

- Docker build error
  ([`8bbb112`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/8bbb112b2cbd179b5dac73f5ea15a66dc9f7ea82))

- Missinggreenlet errors when FastAPI serializes the response
  ([`4542dae`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/4542daef83fcbade3aaebcb3d2a7cf3681b2556a))

- Models be and fe library issues
  ([`7e94854`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/7e948546f8fcaa2e137b27d279ddf3cd45a669cd))

- Resolve chat session synchronization issue
  ([`1e3ce88`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/1e3ce88a558388a98172d4b079822bdd4ca12e6f))

### Chores

- Remove lib from git ignore and retry ghcr workflow
  ([`18e262e`](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/commit/18e262e5418de54079b83d26b2737303127168b4))

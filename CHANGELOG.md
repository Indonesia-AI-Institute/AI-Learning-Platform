# CHANGELOG


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

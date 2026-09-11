---
name: release
description: Explain or verify this repo's release pipeline — how conventional commits map to version bumps, what happens on merge to main (semantic-release -> re-test -> image build+push; there is no automated deploy), and how to check what the next version would be. Use when asked about releasing, versioning, cutting a release, what version a change would trigger, or how a new image actually gets deployed after a merge.
---

# Release pipeline

There is no manual release step — `python-semantic-release` (PSR) runs
in `.github/workflows/release.yml`'s `release` job on every push to
`main` (not on PRs) and decides everything from commit messages since
the last tag. This skill is about understanding and verifying that
pipeline, not about performing a release yourself — there's no local
command that safely triggers one (see "Don't" below).

Five workflow files divide the CI/release responsibilities — know which
one is relevant to what you're asked about:

| File | Trigger | Does |
|---|---|---|
| `test-unit.yml` | `workflow_call` only, never triggered directly | Backend + frontend unit-test jobs, shared by the three below |
| `test-integration.yml` | `workflow_call` only, never triggered directly | Backend + frontend integration-test jobs (real Postgres service container). A separate file from unit, not one job gated by a scope input — that would leave every caller showing the other scope's jobs as permanently skipped in the checks UI |
| `test.yml` | every push, any branch except `main` | Calls `test-unit.yml` only — fast feedback, no DB. Excludes `main` deliberately, see `release.yml` below |
| `pr-validate.yml` | every PR into `main` | Calls both `test-unit.yml` and `test-integration.yml` -> if both pass, a real (unpushed) Docker build of both images |
| `release.yml` | push to `main` | PSR -> if a version was cut, calls both `test-unit.yml` and `test-integration.yml` again -> build+push the final images |

## How a version gets decided

PSR reads every commit message since the last tag using the Angular
convention (`<type>: <description>`, or `<type>(<scope>): <description>`).
The mapping, from the **repo-root** `pyproject.toml`'s
`[tool.semantic_release.commit_parser_options]` (this one file's config
governs versioning for the **whole repo**, not just the backend — both
the `-api` and `-frontend` GHCR images get tagged with the same version;
it lives at the root specifically so it isn't misread as backend-only):

| Commit type | Effect |
|---|---|
| `feat` | minor bump |
| `fix`, `perf`, `refactor` | patch bump |
| `docs`, `style`, `test`, `chore`, `ci`, `build`, `revert` | no bump — recognized, but doesn't trigger a release by itself |
| A `BREAKING CHANGE:` footer, or `!` after the type (`feat!:`) | major bump |

If every commit since the last tag is a no-bump type, PSR publishes
nothing — the `release` job's `released` output is `false`, and the
`test-unit`/`test-integration`/`build-api`/`build-frontend` jobs in
`release.yml` after it (which all depend on that output) skip entirely,
whether or not the PR itself was substantial. A PR that should ship a
real version needs at least one `feat`/`fix`/`perf`/`refactor` commit in
it — a title alone doesn't count, since PSR reads the actual commit
history, not the PR title.

## Checking what the next version would be (safe, read-only)

```bash
pip install python-semantic-release==9.*
semantic-release --config pyproject.toml version --print
```

This prints the version PSR would cut without creating a tag, pushing
anything, or modifying `CHANGELOG.md` — safe to run any time out of
curiosity or to sanity-check a PR before merging. Run it from the repo
root — the config path is relative to wherever you invoke it from.

## What happens after a version is published (informational — this is CI's job)

1. `release` job (`release.yml`): PSR tags `main`, updates
   `CHANGELOG.md`, pushes both back to the repo, and creates a GitHub
   Release for the new tag (release notes come from the same changelog
   template as `CHANGELOG.md`) — see `gh release list` / the repo's
   Releases page.
2. `test-unit` / `test-integration` jobs: only run if `released ==
   'true'`. Re-run both `test-unit.yml` and
   `test-integration.yml` — the same tests that already ran on the
   PR that got merged — as a final sanity gate
   immediately before building a shippable image. This deliberately
   duplicates the PR-time run rather than trusting it alone, because
   nothing currently enforces that PR check passing before a merge is
   allowed (see "Don't" below) — this is the actual last gate before a
   real, tagged image ships.
3. `build-api` / `build-frontend`: only run if both post-release test
   jobs succeeded. Build and push
   `ghcr.io/indonesia-ai-institute/ai-learning-platform-{api,frontend}`,
   tagged `latest`, the exact version, and `{major}.{minor}` / `{major}`
   convenience tags.
4. `update-release-notes`: only runs if both images pushed successfully.
   Appends a `## Images` section listing the exact `image:version`
   references to the GitHub Release body created in step 1 — the release
   is created before the images exist, so this is a follow-up edit
   (`gh release edit`), not part of the original creation.

That's the end of the automated pipeline — there is no CD step. Getting
a new image onto a real host is a manual `docker compose -f
docker-compose.prod.yml pull && up -d` (see the root README's "Docker:
With the Repository" section). A `deploy.yml` workflow that SSHed into a
production host and did this automatically existed at one point and was
deliberately removed — see the root `CLAUDE.md`'s "Known, deliberately
deferred gaps".

## Don't

- Don't run `semantic-release ... publish` locally — it pushes a tag and
  a `CHANGELOG.md` commit to `main` and (per the `[tool.semantic_release.remote]`
  config) talks to GitHub using a `GH_TOKEN`. This is CI's job, gated on
  an actual merge to `main`; doing it locally bypasses that gate and can
  desync the tag from what's actually on `main`.
- Don't hand-edit `CHANGELOG.md` or the version in `src/backend/pyproject.toml`
  — both are generated/written by PSR (from the root `pyproject.toml`'s
  config). A manual edit will be inconsistent with what PSR computes on
  the next run.
- Don't assume a merged PR shipped a new version — check whether it
  contained a bump-worthy commit type (see the table above) before
  telling anyone a change is live.
- Don't assume a passing PR check means the merge is safe to make blindly
  — CI runs tests now, but no branch protection rule currently requires
  them to pass before merging, and none can be configured yet: this repo
  is private on a GitHub plan where both classic branch protection and
  rulesets are unavailable (root `CLAUDE.md` Critical Rule 3).

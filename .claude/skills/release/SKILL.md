---
name: release
description: Explain or verify this repo's release pipeline — how conventional commits map to version bumps, what happens on merge to main (through image build+push; there is no automated deploy), and how to check what the next version would be. Use when asked about releasing, versioning, cutting a release, what version a change would trigger, or how a new image actually gets deployed after a merge.
---

# Release pipeline

There is no manual release step — `python-semantic-release` (PSR) runs
in `.github/workflows/container-build.yml`'s `release` job on every push
to `main` (not on PRs) and decides everything from commit messages since
the last tag. This skill is about understanding and verifying that
pipeline, not about performing a release yourself — there's no local
command that safely triggers one (see "Don't" below).

## How a version gets decided

PSR reads every commit message since the last tag using the Angular
convention (`<type>: <description>`, or `<type>(<scope>): <description>`).
The mapping, from `src/backend/pyproject.toml`'s
`[tool.semantic_release.commit_parser_options]` (this one file's config
governs versioning for the **whole repo**, not just the backend — both
the `-api` and `-frontend` GHCR images get tagged with the same version):

| Commit type | Effect |
|---|---|
| `feat` | minor bump |
| `fix`, `perf`, `refactor` | patch bump |
| `docs`, `style`, `test`, `chore`, `ci`, `build`, `revert` | no bump — recognized, but doesn't trigger a release by itself |
| A `BREAKING CHANGE:` footer, or `!` after the type (`feat!:`) | major bump |

If every commit since the last tag is a no-bump type, PSR publishes
nothing — the `release` job's `released` output is `false`, and
`build-api`/`build-frontend` (which both depend on it) skip pushing new
images entirely, whether or not the PR itself was substantial. A PR that
should ship a real version needs at least one `feat`/`fix`/`perf`/`refactor`
commit in it — a title alone doesn't count, since PSR reads the actual
commit history, not the PR title.

## Checking what the next version would be (safe, read-only)

```bash
pip install python-semantic-release==9.*
semantic-release --config src/backend/pyproject.toml version --print
```

This prints the version PSR would cut without creating a tag, pushing
anything, or modifying `CHANGELOG.md` — safe to run any time out of
curiosity or to sanity-check a PR before merging.

## What happens after a version is published (informational — this is CI's job)

1. `release` job: PSR tags `main`, updates `CHANGELOG.md`, pushes both
   back to the repo.
2. `build-api` / `build-frontend`: build and push
   `ghcr.io/indonesia-ai-institute/ai-learning-platform-{api,frontend}`,
   tagged `latest`, the exact version, and `{major}.{minor}` / `{major}`
   convenience tags.

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
  — both are generated/written by PSR. A manual edit will be inconsistent
  with what PSR computes on the next run.
- Don't assume a merged PR shipped a new version — check whether it
  contained a bump-worthy commit type (see the table above) before
  telling anyone a change is live.

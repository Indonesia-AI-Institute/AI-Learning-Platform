---
name: open-pr
description: Commit staged/working changes, push the branch, and open a pull request following this repo's established conventions — conventional commit messages, a Summary + Test plan PR body, and a check that local main isn't stale before trusting the diff. Use when asked to commit and push and open a PR, or to "ship" the current changes.
---

# Open a PR

Codifies the exact workflow already used for this repo's PRs so it
doesn't need re-deriving each time, and so the one subtle failure mode
already hit once — a stale local `main` producing a misleading diff —
doesn't happen again silently.

## Steps

1. **Review what's actually changing** before staging anything:
   ```bash
   git status
   git diff
   ```
   Stage specific files/directories, not a blanket `git add -A` — if
   `git status` shows anything unexpected (a `.env`/`.env.be`/`.env.fe`
   file, an untracked file you don't recognize as yours from this
   session), stop and ask rather than sweeping it in. Never commit a real
   `.env*` file — only the `.example` variants are meant to be tracked.

2. **Confirm the branch name and commit message fit this repo's
   convention** (see the root `CLAUDE.md`'s "Conventions" section):
   branch `chore/<area>-<what>` for tidy-up/infra, otherwise
   `feat|fix/<short-description>`; commit messages in Angular/
   conventional-commit style (`feat|fix|perf|refactor|docs|style|test|chore|ci|build|revert: ...`)
   since `python-semantic-release` reads these on `main` to decide the
   next version (see the `release` skill) — a vague message doesn't
   break anything but produces a useless changelog entry.

3. **Commit** with a message ending in the attribution line from this
   session's system instructions, if one is present.

4. **Before pushing, check whether local `main` is stale relative to
   `origin/main`** — this happened for real once, where a merged PR's
   commits kept showing up as "part of" a later, unrelated PR's diff
   because local `main` was several commits behind:
   ```bash
   git fetch origin main
   git log --oneline main..origin/main   # anything here means local main is behind
   ```
   If it's behind, fast-forward it (`git checkout main && git merge --ff-only origin/main && git checkout -`)
   before continuing — don't open a PR against a stale comparison.

5. **Push with upstream tracking:**
   ```bash
   git push -u origin <branch>
   ```

6. **Create the PR** with `gh pr create --base main`, using a body with
   exactly two sections:
   - `## Summary` — bullet points of what changed and *why*, not a
     restatement of the diff. Call out any real bug found and fixed along
     the way (not just features/refactors) — that's been the most useful
     part of past PR descriptions here.
   - `## Test plan` — a checklist of what was actually verified (lint/
     build/test results, anything checked against a real running
     container or a live call), not what *should* work.
   End the body with the attribution line from this session's system
   instructions, if one is present.

7. **After creation, verify mergeability** rather than assuming success
   from a non-error exit:
   ```bash
   gh pr view <number> --json mergeable,mergeStateStatus,changedFiles
   ```
   `mergeable: MERGEABLE` is what matters; `mergeStateStatus: UNSTABLE`
   right after creation usually just means CI checks haven't finished
   yet, not a real problem — don't conflate the two. `changedFiles` is a
   quick sanity check that the diff size looks like what was actually
   intended (a much larger or smaller number than expected is worth a
   second look before telling the user it's ready).

8. **Report the PR URL** and the mergeability check's result plainly.

## Notes

- Never force-push, never skip hooks (`--no-verify`), never amend a
  commit that's already been pushed — see the root system instructions'
  git safety rules, which apply here without exception.
- If `gh` isn't authenticated via `gh auth status`, this repo has
  previously worked around a `read:org`-scope failure in
  `gh auth login --with-token` by exporting the same OAuth token
  `git credential fill` already has as `GH_TOKEN` for individual `gh`
  commands instead — full login isn't required just to create a PR.

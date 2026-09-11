---
name: docs-sync-check
description: Audit CLAUDE.md/README.md files across the repo against actual repo state — every referenced path/script exists where claimed, skill frontmatter names match their directory, documented env vars match what the code actually reads, and no duplicated logic has silently drifted apart. Use when asked to check for stale docs, verify documentation accuracy, or as a final pass before a release.
---

# Docs-sync check

This repo has a specific, repeated failure mode worth checking for
deliberately: documentation (or a compose file, or a config default)
correctly described reality *when written*, then reality moved on
without it. Every item below is something that actually happened here,
not a hypothetical:

- `deploy.sh` was documented/assumed to live at the repo root, but was
  actually sitting in `.github/workflows/deploy.sh` — would have broken
  every real production deploy, found only by manually tracing
  `deploy.yml`'s SSH script.
- A root `.env`/`.env.example` mechanism was built, documented in three
  files, then deliberately removed — and two of those three references
  were still pointing at it afterward.
- `formatDuration` and a `PROMPT_TYPES`-shaped table were independently
  duplicated across frontend files instead of reused, invisible until a
  side-by-side review.
- A stale `msw` entry sat in `package.json`'s `trustedDependencies` long
  after the package it referred to was removed from the dependency tree.

## Steps

1. **Collect every path, filename, and command referenced by a `CLAUDE.md`
   or `README.md`** in the repo (root, `src/backend/`, `src/frontend/`).
   For each one that names a file/script/directory, confirm it actually
   exists at that path:
   ```bash
   find . -iname "CLAUDE.md" -o -iname "README.md" | grep -v node_modules
   ```
   Then for each doc, extract backtick-quoted paths and check them —
   don't just skim for obviously-wrong ones, actually verify each.

2. **Confirm every skill's `name:` frontmatter field matches its
   directory name**, across all three `.claude/skills/` trees (root,
   backend, frontend) — a mismatch means the skill won't be found by its
   documented name:
   ```bash
   for f in .claude/skills/*/SKILL.md src/backend/.claude/skills/*/SKILL.md src/frontend/.claude/skills/*/SKILL.md; do
     dir=$(basename "$(dirname "$f")")
     name=$(grep -m1 "^name:" "$f" | cut -d' ' -f2)
     [ "$dir" != "$name" ] && echo "MISMATCH: $f (dir=$dir, name=$name)"
   done
   ```

3. **Check every README's skill list is actually complete and accurate**
   — cross-reference the skill names each README enumerates in its
   "Claude Code Project Tooling" section against what's actually present
   in that project's `.claude/skills/` directory. A skill added without
   updating the README list (or a skill removed without pruning it) is
   exactly the class of drift this check exists for.

4. **Spot-check documented env vars against what the code reads.** For
   each variable a README/CLAUDE.md table claims is required or has a
   specific default, grep for where it's actually read
   (`os.environ`/`Settings` field in the backend, `process.env`/
   `window.__ENV__` in the frontend) and confirm the description still
   matches — a default that changed in code but not in docs, or a
   variable removed from code but still documented, are both real finds
   here.

5. **Look for logic that appears near-identically in two or more
   places** — this is harder to automate than the checks above, but a
   quick `grep` for a distinctive string from one file's implementation
   across the rest of the codebase catches the exact class of bug that
   produced the `formatDuration`/`PROMPT_TYPES` duplication. Flag it as a
   `modularize` candidate rather than fixing it inline unless asked.

6. **Report every finding concretely**: the doc file, the line, what it
   claims, and what's actually true. If everything checks out, say so
   plainly rather than padding the report — this is a verification pass,
   not a creative-writing exercise.

## Notes

- This is a read-heavy, judgment-light skill — most of its value is in
  actually doing the grep/find sweeps above rather than reasoning about
  what "might" be stale. Don't skip the sweeps and go straight to
  eyeballing files that look suspicious.
- Fix what you find unless the fix itself is a real design decision (like
  the `.env.example` removal was) — a broken path reference or an
  obviously-outdated default is safe to correct directly; report design
  ambiguity rather than guessing.

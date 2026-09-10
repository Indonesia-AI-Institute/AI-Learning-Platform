---
name: db-migrate
description: Generate an Alembic migration from current model changes, then review it for correctness (renames, data migrations, downgrade sanity) before applying. Use when asked to create, generate, or review a database migration.
---

# Database migration

Generate and review a migration for whatever model change was described
in this invocation.

## Steps

1. **Confirm a reachable Postgres** at the `DATABASE_URL` currently
   configured (`.env.be` at the repo root, or whatever's exported) — the
   database must exist and have the current migration chain already
   applied (`alembic upgrade head`) for autogenerate to diff against the
   right baseline.

2. **Generate the migration:**
   ```bash
   cd src/backend && uv run alembic revision --autogenerate -m "<short description>"
   ```

3. **Read the generated file** in `src/backend/alembic/versions/` in
   full before doing anything else. Autogenerate is not reliable for:
   - **Column/table renames** — it will emit a `drop` + `add` (data
     loss) instead of a rename. If the actual change was a rename, hand-edit
     the migration to use `op.alter_column(..., new_column_name=...)` or
     `op.rename_table(...)` instead.
   - **Server-side defaults and check constraints** — verify these
     actually match what the model declares; autogenerate sometimes
     misses or misrepresents them.
   - **Data migrations** — a schema change that needs existing rows
     backfilled (e.g. a new `NOT NULL` column) needs a manual `op.execute(...)`
     or Python data migration step added — autogenerate only handles
     schema, never data.

4. **Check `upgrade()` and `downgrade()` are both sensible.** A
   `downgrade()` that's just `pass` when the `upgrade()` did something
   real is usually wrong, not intentional — flag it rather than leaving
   it silently broken.

5. **Apply it locally and confirm it runs cleanly**, both directions:
   ```bash
   uv run alembic upgrade head
   uv run alembic downgrade -1
   uv run alembic upgrade head
   ```

6. **Report back**: the migration file path, a plain-English summary of
   what it does, and explicitly flag anything from step 3's checklist
   that needed hand-editing versus what autogenerate produced correctly
   on its own.

Do not silently "fix" a migration that looks wrong and move on without
saying so — a schema change is exactly the kind of thing that should be
visibly reviewed, not quietly patched.

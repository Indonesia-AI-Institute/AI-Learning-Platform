---
name: new-model
description: Scaffold a brand-new SQLAlchemy model — the table + relationships + repository + registering it for Alembic to see. Use when asked to add a new database table/resource, as opposed to a new endpoint on an existing one (see new-endpoint for that, which assumes the model already exists).
---

# New backend model

`new-endpoint` starts at "add a schema," assuming the underlying table
already exists. This skill is the step before that — a genuinely new
resource, not new behavior on an existing one.

Read `src/backend/CLAUDE.md` first if you haven't already this session.

## Steps

1. **Create the model** in `src/backend/models/<resource>.py`, extending
   `BaseModel` (`src/backend/models/base.py`) — it already provides a
   UUID primary key and `created_at`/`updated_at`. Add `SoftDeleteMixin`
   too only if this resource genuinely needs soft-delete (most don't;
   check a sibling model before assuming it does). Use
   `sqlalchemy.dialects.postgresql.UUID(as_uuid=True)` for any foreign
   key — this codebase's models are Postgres-specific by design (see
   `src/backend/CLAUDE.md`'s note that tests need real Postgres, not
   SQLite, for exactly this reason). Follow `models/task.py` as the
   template for column and `relationship(..., back_populates=...)` style.

2. **Register the model in `src/backend/models/__init__.py`** — add an
   `from .<resource> import <Resource>` line. **This step is easy to
   forget and fails silently**: Alembic's `revision --autogenerate`
   detects new tables by importing everything `models/__init__.py`
   imports, not by scanning the `models/` directory. Skip this and
   `db-migrate`'s autogenerate step will produce an empty migration for
   your new table with no error explaining why.

3. **Add the reverse side of any relationship** on the model(s) it
   references (a `relationship(..., back_populates="...")` on both ends,
   not just the new model's side) — check every model named in a
   `ForeignKey(...)` call and add the matching relationship there too.

4. **Create the repository** in
   `src/backend/repositories/<resource>_repository.py`, extending
   `BaseRepository[<Resource>]` (generic `create`/`get`/`get_all`/
   `update`/`delete`/`filter_by` come for free) — add custom query
   methods only for what the generic methods don't cover, following
   `TaskRepository`'s style.

5. **Generate and review the initial migration** — use the `db-migrate`
   skill now that the model is registered. Confirm the generated
   migration actually creates the new table (if it comes back empty,
   step 2 was likely missed).

6. **From here, use `new-endpoint`** for the schema/service/route layer
   on top of this new model.

## Before finishing

Confirm `alembic upgrade head` applies cleanly against a fresh database,
not just an already-migrated one — a new model with a bad `ForeignKey`
target (wrong table name, typo) fails at migration-apply time, not at
Python-import time, so a clean `import` doesn't prove the schema is
correct.

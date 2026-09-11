---
name: new-config-var
description: Add a new environment-configurable setting correctly — Settings field, .env.be.example entry, confirm it's actually read where intended, and a test proving both states of a toggle behave differently. Use when asked to add a new config option, feature flag, or environment variable to the backend.
---

# New backend config variable

This exact class of bug has shipped **twice** in this codebase: a config
field that exists in `Settings`, looks fully wired up, and does
nothing — `HOST`/`PORT` were declared while `entrypoint.sh` had them
hardcoded, and `ENABLE_BANLIST_FILTER` existed while
`LLMService._check_banlist` ran unconditionally, never checking it. Both
were invisible to every test that didn't specifically assert the
toggle's effect, and invisible to static review. This skill exists
specifically to make a third occurrence harder.

A related, lower-severity version of the same pattern already sits in
this codebase today: `ENABLE_RAG`/`ENABLE_WEBSEARCH` are declared in
`Settings` with a test asserting their *default value*, but have no
implementation anywhere to gate — there's nothing to "wire up" yet since
the features themselves don't exist. That's a legitimate placeholder for
future work, not a bug, but it's a useful contrast: know which case
you're in before adding a new one.

## Steps

1. **Add the field to `Settings`** (`src/backend/core/config.py`), typed
   correctly (`bool` for a toggle, not `str = "true"`), with a sensible
   default. If it's required with no safe default (like `SECRET_KEY`,
   `CORS_ORIGINS`), add a `@field_validator` that raises with a message
   telling the operator exactly what to set and why — follow
   `validate_secret_key`'s pattern.

2. **Add it to `.env.be.example`** with a one-line comment explaining
   what it does and, if not obvious, why the default is what it is.
   Group it near related settings (feature flags near `ENABLE_RAG`/
   `ENABLE_WEBSEARCH`/`ENABLE_BANLIST_FILTER`, not appended at the end
   of the file regardless of topic).

3. **Find where this value needs to actually change behavior, and grep
   for it there before writing any code** — if you're about to add
   `ENABLE_SOMETHING` intending to gate a specific service method, run
   `grep -rn "def method_name" src/backend/services/` first and confirm
   you're editing the actual call path, not a copy or an unrelated
   method with a similar name.

4. **Read the setting where it's supposed to matter** — `from backend.core.config
   import settings` and an explicit `if settings.ENABLE_SOMETHING:` (or
   equivalent) at the point of use. Don't just add the field and assume
   a future commit will wire it up — if the wiring isn't part of this
   change, say so explicitly rather than leaving a plausible-looking but
   inert field.

5. **Write a test that asserts both states produce different behavior**,
   not just that the field parses and defaults correctly — see
   `tests/unit/test_llm_service.py` for the pattern
   (`ENABLE_BANLIST_FILTER` toggle test). A test that only checks
   `Settings(...).ENABLE_SOMETHING is True` would have passed even when
   `ENABLE_BANLIST_FILTER` was completely unread; it proves the field
   exists, not that anything listens to it.

6. **If this is a secret or deployment-specific value** (an API key, a
   URL, anything that shouldn't be the same across environments), also
   check whether it needs equivalent documentation in the root
   `README.md`'s Environment Variables table, and whether
   `docker-compose.prod.yml`/`docker-compose.yml` need it passed through
   (they read the whole `.env.be` file via `env_file:`, so a new var
   there needs no compose-file change — but double check nothing
   hardcodes an override for it in either compose file).

## Before finishing

Run the backend's `check` (or `test`) skill. Confirm specifically that
the new test added in step 5 fails if you temporarily comment out the
`if settings.ENABLE_SOMETHING:` guard — if it doesn't fail, the test
isn't actually testing the wiring, only the field's existence.

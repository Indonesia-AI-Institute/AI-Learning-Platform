---
name: new-guardrail
description: Scaffold a new content-safety guardrail (filter class, config toggle, wiring into LLMService, tests) following this codebase's conventions. Use when asked to add a new guardrail, content filter, or moderation check for chat/LLM input.
---

# New guardrail

Scaffold a new guardrail for whatever check was described in this
invocation (e.g. "a PII filter", "a profanity classifier", "a
prompt-length-anomaly check").

Read `src/backend/CLAUDE.md` first if you haven't already this session.

## What a guardrail is here

A pre-flight check run against user-supplied text before it reaches an
LLM provider, that can reject the request by raising. The only existing
example is `guardrails/banlist_filter.py` (`BanListFilter`) — a
Unicode-normalized keyword substring match, wired into `LLMService`.

**Guardrails in this codebase are explicitly defense-in-depth, not a
hard safety guarantee.** `BanListFilter`'s own module docstring says so
directly — match that honesty. If the new guardrail is meant to be a
real moderation boundary (not "catches the obvious cases"), say so
explicitly in its docstring and to the user; don't imply a stronger
guarantee than a simple filter can actually provide.

## What to build, in order

1. **Filter class** in `guardrails/<name>_filter.py`. Follow
   `BanListFilter`'s shape unless the new check genuinely needs a
   different result shape:
   ```python
   class <Name>Filter:
       def __init__(self, ...config...):
           ...

       def check(self, text: str) -> Tuple[bool, ...]:
           """Returns (is_blocked, <detail>)."""
           if not text:
               return False, ...
           ...
   ```
   If the check's natural output isn't a simple bool (e.g. a moderation
   classifier returning categories + confidence), that's fine — just
   keep `check(text)` as the entry point so it composes the same way in
   `LLMService`, and document the actual return shape clearly.

2. **Config toggle** in `core/config.py`'s `Settings`, following the
   existing `ENABLE_BANLIST_FILTER` / `BANNED_KEYWORDS` pattern:
   ```python
   ENABLE_<NAME>_FILTER: bool = True
   # plus whatever config the filter itself needs
   ```

3. **Wire it into `llm/services/llm_service.py`** — instantiate in
   `LLMService.__init__` alongside `self.banlist_filter`, add a
   `_check_<name>(self, text: str)` method mirroring `_check_banlist`,
   and call it from **both** `generate()` and `stream_generate()`
   alongside the existing `_check_banlist(user_text)` call.

   **The toggle must actually gate the check — check it and return
   early if disabled, exactly like this:**
   ```python
   def _check_<name>(self, text: str):
       if not settings.ENABLE_<NAME>_FILTER:
           return
       ...
   ```
   `ENABLE_BANLIST_FILTER` existed in `Settings` for a long time without
   `_check_banlist` ever actually reading it — the filter always ran
   regardless of the toggle's value. Don't repeat that: write the
   `if not settings.ENABLE_<NAME>_FILTER: return` guard first, before
   filling in the actual check logic, so it's structurally impossible to
   forget.

4. **Decide and document the check's scope explicitly.** The existing
   `_check_banlist` only scans the concatenated content of `role ==
   "user"` messages — it does not see the system prompt, and (following
   the `_inject_system_prompt` fix — see the `new-agent` skill and
   Critical Rule #3 in `CLAUDE.md`) it also does not see any
   caller-supplied `system`-role messages that survive past
   `messages[0]` after injection. If the new guardrail is meant to catch
   more than literal user chat text — e.g. anything an attacker could
   use to influence the prompt — it needs to explicitly decide what to
   scan, not silently inherit `_check_banlist`'s user-text-only
   assumption. State the chosen scope in the method's docstring.

5. **Tests** in `tests/unit/test_<name>_filter.py`, mirroring the depth
   of `tests/unit/test_banlist_filter.py`: the core check logic (positive
   match, negative/clean input, empty input, any normalization edge
   cases), plus config/mutation methods if the filter has any.

   **Also add the enable-toggle regression test** in
   `tests/unit/test_llm_service.py` (or extend it) — one test proving
   the check blocks when `ENABLE_<NAME>_FILTER=True`, one proving it's a
   no-op when `False`. This is the exact test shape that would have
   caught the `ENABLE_BANLIST_FILTER` gap immediately.

## Before finishing

Use the `test` skill to run `tests/unit/` (no database needed for any of
this) and confirm everything passes.

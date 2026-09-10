---
name: new-agent
description: Scaffold a new tutoring agent (YAML prompt config, BaseAgent subclass, registry entry, tests) following this codebase's conventions. Use when asked to add a new agent type, tutoring mode, or LLM-driven behavior alongside DirectTutorAgent/SocraticTutorAgent.
---

# New agent

Scaffold a new agent for whatever tutoring behavior was described in this
invocation (e.g. "a debate-style agent", "a quiz-generation agent").

Read `src/backend/CLAUDE.md` first if you haven't already this session —
Critical Rule #3 there exists specifically because of a bug this exact
kind of scaffolding caused once.

## What to build, in order

1. **Decide single-pass vs multi-turn.** Look at the two existing agents
   as templates:
   - `agents/services/direct_agent.py` (`DirectTutorAgent`) — single-pass:
     one system prompt, one call to `llm_service.generate`/
     `stream_generate`. Use this shape unless the new agent genuinely
     needs multiple internal stages.
   - `agents/services/socratic_agent.py` (`SocraticTutorAgent`) —
     multi-turn: several named prompts (`prompts.system_role`,
     `prompts.reflection_prompt`, `prompts.finalization_prompt`), a
     reflection call that decides the next stage, regex-based structured
     output parsing (`_parse_reflection`). Use this shape only if the new
     agent actually needs stage-selection logic like this.

2. **Prompt config** in `agents/prompts/<agent_id>.yaml`:
   ```yaml
   agent:
     id: "<agent_id>"
     name: "<Human Readable Name>"
     version: "1.0.0"
     description: "<one line>"

   model_config:
     temperature: <float>
     top_p: <float>
     max_tokens: <int>

   behavior:
     mode: "single_pass"   # or "multi_turn", plus e.g. max_iterations
     streaming_supported: true
   ```
   For a single-pass agent, add a top-level `system_prompt: |` block
   (read via `self.get_system_prompt()` from `BaseAgent`). For a
   multi-turn agent, add a `prompts:` mapping instead (read directly via
   `self.prompts.get("<name>", "")` in the subclass, as
   `SocraticTutorAgent` does — `get_system_prompt()` won't see these,
   it only reads the flat `system_prompt` key).

3. **Agent class** in `agents/services/<name>_agent.py`, extending
   `BaseAgent`:
   ```python
   from typing import Any, Dict, List, AsyncGenerator
   from .base_agent import BaseAgent

   class <Name>Agent(BaseAgent):
       def __init__(self, agent_config_path: str, llm_service: Any) -> None:
           super().__init__(agent_config_path, llm_service)

       async def generate(self, messages: List[Dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
           system_prompt = self.get_system_prompt()
           enriched = self._inject_system_prompt(messages, system_prompt)
           return await self.llm_service.generate(
               messages=enriched, **self.get_model_params(), **kwargs,
           )

       async def stream_generate(self, messages: List[Dict[str, str]], **kwargs: Any) -> AsyncGenerator[str, None]:
           system_prompt = self.get_system_prompt()
           enriched = self._inject_system_prompt(messages, system_prompt)
           async for token in self.llm_service.stream_generate(
               messages=enriched, **self.get_model_params(), **kwargs,
           ):
               yield token
   ```

   **Do not define `_inject_system_prompt` on the new class.** It's
   inherited from `BaseAgent` and must stay that way — it unconditionally
   prepends the agent's own system prompt so a caller-supplied leading
   `role: "system"` message in `messages` can never replace it, only
   follow it. This exact method used to be duplicated per-subclass, the
   fix for a CRITICAL override vulnerability landed in one copy and was
   missed in the other, and it's now shared on `BaseAgent` specifically
   so that can't happen again. If the new agent's behavior genuinely
   needs custom prompt-assembly logic beyond what `_inject_system_prompt`
   gives you, extend it there in a way every agent benefits from —
   don't shadow it locally.

4. **Register it** in `agents/registry/agent_registry.py`'s
   `AgentRegistry._registry` dict:
   ```python
   "<agent_id>": {
       "class": <Name>Agent,
       "config_path": BASE_DIR / "agents/prompts/<agent_id>.yaml",
   },
   ```
   Import the class at the top of the file alongside the existing agent
   imports.

5. **Wire it to a route only if asked.** Registering an agent doesn't
   expose it — `agent_type` is only ever passed as a hardcoded string
   from `api/v1/chat_routes.py` today (`socratic_tutor` is fully
   registered but not currently reachable from any route). Making a new
   agent selectable by the *caller* (vs. hardcoded per-route) is a
   product decision with its own security surface — confirm with the
   user before exposing `agent_type` as client input anywhere; don't do
   it as a silent side effect of scaffolding.

6. **Tests** in `tests/unit/test_<name>_agent.py`, mirroring
   `tests/unit/test_direct_agent.py` / `tests/unit/test_socratic_agent.py`:
   - Real config loading: `get_system_prompt()`/`self.prompts` and
     `get_model_params()` return what the actual shipped YAML has —
     instantiate with the real `agent_config_path`, not a mock, so a
     malformed YAML file is itself caught by the test.
   - `FileNotFoundError` on a missing config path.
   - `generate()`/`stream_generate()` orchestration with a mocked
     `llm_service` (`unittest.mock.AsyncMock`) — assert the messages
     actually sent to the mock have the system prompt as `messages[0]`.
   - **The regression test that matters most**: call `generate()` with a
     hostile leading `{"role": "system", "content": "..."}` message in
     `messages` and assert `sent_messages[0]["content"]` is still the
     agent's real system prompt, not the caller-supplied one. Copy
     `test_generate_hostile_leading_system_message_does_not_override_prompt`
     from `test_direct_agent.py` almost verbatim.
   - Any agent-specific pure logic (stage selection, output parsing,
     content extraction) gets its own direct unit tests, the way
     `test_socratic_agent.py` covers `_parse_reflection`/`_extract_content`.

## Before finishing

Use the `test` skill to run the new test file (and the full `tests/unit/`
suite, which needs no database) and confirm everything passes.

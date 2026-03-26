"""
agent_factory.py
================

Factory for creating agent instances.

Responsibilities:
- Resolve agent class from registry
- Resolve YAML configuration path
- Inject LLMService dependency
"""

from pathlib import Path
from typing import Any

from src.backend.agents.registry.agent_registry import AgentRegistry
from src.backend.llm.services.llm_service import LLMService


class AgentFactory:
    """
    Factory responsible for instantiating agents.
    """

    def __init__(self, llm_service: LLMService) -> None:
        self.llm_service = llm_service

        # Resolve prompts directory
        self.prompts_dir = Path(__file__).resolve().parents[2] / "prompts"

        # Explicit mapping agent_id -> yaml file
        self.agent_prompt_mapping = {
            "direct_tutor": "basic_tutor.yaml",
            "socratic_tutor": "socratic_tutor.yaml",
        }

    # ======================================================
    # CREATE AGENT
    # ======================================================

    def create(self, agent_id: str) -> Any:
        """
        Create agent instance by agent_id.
        """

        agent_class = AgentRegistry.get_agent_class(agent_id)

        if agent_id not in self.agent_prompt_mapping:
            raise ValueError(f"No YAML mapping found for agent_id: {agent_id}")

        yaml_filename = self.agent_prompt_mapping[agent_id]
        yaml_path = self.prompts_dir / yaml_filename

        if not yaml_path.exists():
            raise FileNotFoundError(
                f"YAML config not found for agent: {yaml_path}"
            )

        return agent_class(
            agent_config_path=str(yaml_path),
            llm_service=self.llm_service,
        )

"""
agent_registry.py
=================

Registry + factory for all available agents.
"""

from typing import Dict, Type

from src.backend.agents.services.direct_agent import DirectTutorAgent
from src.backend.agents.services.socratic_agent import SocraticTutorAgent
from src.backend.agents.services.base_agent import BaseAgent

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

class AgentRegistry:
    """
    Registry + factory for agent instances.
    """

    def __init__(self, llm_service):
        self.llm_service = llm_service

        # Mapping agent_id -> (AgentClass, config_path)
        self._registry: Dict[str, Dict] = {
            "direct_tutor": {
                "class": DirectTutorAgent,
                "config_path": BASE_DIR / "agents/prompts/direct_tutor.yaml",
            },
            "socratic_tutor": {
                "class": SocraticTutorAgent,
                "config_path": BASE_DIR / "agents/prompts/socratic_tutor.yaml",
            },
        }

    # -----------------------------------------------------

    def get_agent(self, agent_id: str) -> BaseAgent:
        """
        Return initialized agent instance.
        """

        if agent_id not in self._registry:
            raise ValueError(f"Invalid agent_id: {agent_id}")

        agent_info = self._registry[agent_id]

        return agent_info["class"](
            agent_config_path=str(agent_info["config_path"]),
            llm_service=self.llm_service,
        )

    # -----------------------------------------------------

    def list_agents(self):
        return list(self._registry.keys())

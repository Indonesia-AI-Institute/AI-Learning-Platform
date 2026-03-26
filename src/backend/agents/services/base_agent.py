from pathlib import Path
from typing import Any, Dict, List
import yaml
from src.backend.llm.services.llm_service import LLMService


class BaseAgent:

    def __init__(
        self,
        agent_config_path: str,
        llm_service: LLMService,
    ) -> None:

        self.llm_service = llm_service
        self.config = self._load_yaml(agent_config_path)

        self.agent_info = self.config.get("agent", {})
        self.model_config = self.config.get("model_config", {})
        self.behavior_config = self.config.get("behavior", {})
        self.prompts = self.config.get("prompts", {})

    def _load_yaml(self, path: str) -> Dict[str, Any]:
        file_path = Path(path)

        if not file_path.exists():
            raise FileNotFoundError(f"Agent config not found: {path}")

        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get_system_prompt(self) -> str:
        return self.config.get("system_prompt", "")

    def get_model_params(self) -> Dict[str, Any]:
        return {
            "temperature": self.model_config.get("temperature"),
            "top_p": self.model_config.get("top_p"),
            "max_tokens": self.model_config.get("max_tokens"),
        }

    async def generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        raise NotImplementedError(
            "generate() must be implemented in subclass."
        )

    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ):
        raise NotImplementedError(
            "stream_generate() must be implemented in subclass."
        )

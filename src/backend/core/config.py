"""
config.py
=========
"""

from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


def find_project_root(start_path: Path) -> Path:
    markers = [".git", "pyproject.toml", "requirements.txt", ".env", ".env_example"]
    current = start_path.resolve()
    while current != current.parent:
        if any((current / marker).exists() for marker in markers):
            return current
        current = current.parent
    return start_path


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = find_project_root(CURRENT_FILE)

ENV_CANDIDATES = [
    PROJECT_ROOT / ".env",
    PROJECT_ROOT / "src" / ".env",
    CURRENT_FILE.parents[2] / ".env",
]


def load_env_file():
    for env_path in ENV_CANDIDATES:
        if env_path.exists():
            load_dotenv(env_path)
            return env_path
    return None


LOADED_ENV_PATH = load_env_file()


class Settings(BaseSettings):

    # =====================================================
    # APP INFO
    # =====================================================
    APP_NAME: str = "AI Learning Platform Backend"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # =====================================================
    # SERVER
    # =====================================================
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # =====================================================
    # SECURITY
    # =====================================================
    SECRET_KEY: str = ""

    # =====================================================
    # DATABASE
    # =====================================================
    DATABASE_URL: str

    # =====================================================
    # LLM PROVIDER SELECTION
    # =====================================================
    DEFAULT_LLM_PROVIDER: str = "openai"
    DEFAULT_LLM_MODEL: str = "gpt-4o"
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 2048
    DEFAULT_TIMEOUT: int = 60

    # =====================================================
    # OPENAI
    # =====================================================
    OPENAI_API_KEY: str | None = None
    OPENAI_API_BASE: str = "https://api.openai.com/v1"

    # =====================================================
    # OPENROUTER
    # =====================================================
    OPENROUTER_API_KEY: str | None = None
    OPENROUTER_API_BASE: str = "https://openrouter.ai/api/v1"

    # OpenRouter provider routing
    # Comma-separated list: "DeepInfra,SiliconFlow,Chutes"
    # Leave empty to let OpenRouter auto-select cheapest/fastest
    OPENROUTER_PROVIDER_ORDER: str | None = None

    # Allow fallback to other providers if preferred ones are unavailable
    OPENROUTER_ALLOW_FALLBACKS: bool = True

    # Only use providers in OPENROUTER_PROVIDER_ORDER, no fallback
    OPENROUTER_REQUIRE_PROVIDER: bool = False

    # =====================================================
    # GEMINI
    # =====================================================
    GEMINI_API_KEY: str | None = None
    GEMINI_API_BASE: str = "https://generativelanguage.googleapis.com/v1beta/openai"

    # =====================================================
    # ANTHROPIC
    # =====================================================
    ANTHROPIC_API_KEY: str | None = None

    # =====================================================
    # CUSTOM PROVIDER
    # =====================================================
    CUSTOM_LLM_API_KEY: str | None = None
    CUSTOM_LLM_BASE_URL: str | None = None

    # =====================================================
    # STREAMING
    # =====================================================
    STREAM_TIMEOUT_SECONDS: int = 60
    STREAM_KEEP_ALIVE: bool = True
    ENABLE_STREAMING: bool = True

    # =====================================================
    # FEATURE FLAGS
    # =====================================================
    ENABLE_RAG: bool = False
    ENABLE_WEBSEARCH: bool = False

    # =====================================================
    # CORS
    # =====================================================
    CORS_ORIGINS: List[str] = ["*"]

    # =====================================================
    # LOGGING
    # =====================================================
    LOG_LEVEL: str = "INFO"

    # =====================================================
    # GUARDRAIL
    # =====================================================
    ENABLE_BANLIST_FILTER: bool = True
    BANNED_KEYWORDS: list[str] = ["illegal", "exploit", "bypass"]

    model_config = SettingsConfigDict(
        env_file=None,
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
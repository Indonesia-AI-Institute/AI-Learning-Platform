from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


def find_project_root(start_path: Path) -> Path:
    # ".git" is the only reliable repo-root marker — pyproject.toml now lives
    # in src/backend, not the repo root, so it can't be used to detect it.
    markers = [".git"]
    current = start_path.resolve()
    while current != current.parent:
        if any((current / marker).exists() for marker in markers):
            return current
        current = current.parent
    return start_path


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = find_project_root(CURRENT_FILE)

ENV_CANDIDATES = [
    PROJECT_ROOT / ".env.be",
    PROJECT_ROOT / ".env",
    CURRENT_FILE.parents[1] / ".env",
]


def load_env_file():
    for env_path in ENV_CANDIDATES:
        if env_path.exists():
            load_dotenv(env_path)
            return env_path
    return None


LOADED_ENV_PATH = load_env_file()


class Settings(BaseSettings):

    APP_NAME: str = "AI Learning Platform Backend"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    SECRET_KEY: str = ""

    DATABASE_URL: str

    DEFAULT_LLM_PROVIDER: str = "openai"
    DEFAULT_LLM_MODEL: str = "gpt-4o"
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 2048
    DEFAULT_TIMEOUT: int = 60

    OPENAI_API_KEY: str | None = None
    OPENAI_API_BASE: str = "https://api.openai.com/v1"

    OPENROUTER_API_KEY: str | None = None
    OPENROUTER_API_BASE: str = "https://openrouter.ai/api/v1"

    # Comma-separated list: "DeepInfra,SiliconFlow,Chutes"
    # Leave empty to let OpenRouter auto-select cheapest/fastest
    OPENROUTER_PROVIDER_ORDER: str | None = None

    # Allow fallback to other providers if preferred ones are unavailable
    OPENROUTER_ALLOW_FALLBACKS: bool = True

    # Only use providers in OPENROUTER_PROVIDER_ORDER, no fallback
    OPENROUTER_REQUIRE_PROVIDER: bool = False

    GEMINI_API_KEY: str | None = None
    GEMINI_API_BASE: str = "https://generativelanguage.googleapis.com/v1beta/openai"

    ANTHROPIC_API_KEY: str | None = None

    CUSTOM_LLM_API_KEY: str | None = None
    CUSTOM_LLM_BASE_URL: str | None = None

    STREAM_TIMEOUT_SECONDS: int = 60
    STREAM_KEEP_ALIVE: bool = True
    ENABLE_STREAMING: bool = True

    ENABLE_RAG: bool = False
    ENABLE_WEBSEARCH: bool = False

    CORS_ORIGINS: List[str] = ["*"]

    LOG_LEVEL: str = "INFO"

    ENABLE_BANLIST_FILTER: bool = True
    BANNED_KEYWORDS: list[str] = ["illegal", "exploit", "bypass"]

    model_config = SettingsConfigDict(
        env_file=None,
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()

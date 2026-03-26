"""
config.py
=========

Application configuration loader menggunakan Pydantic Settings.

Tujuan:
- Load config dari .env
- Centralized config management
- Type-safe configuration
- Future ready untuk scaling (DB, RAG, multi provider)

Scope Saat Ini:
✔ OpenAI LLM Config
✔ App Metadata
✔ CORS
✔ Guardrail Config
"""

from pathlib import Path
from typing import List
import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


# =========================================================
# PROJECT ROOT DETECTOR
# =========================================================

def find_project_root(start_path: Path) -> Path:
    """
    Naik folder sampai ketemu salah satu marker project.
    """

    markers = [
        ".git",
        "pyproject.toml",
        "requirements.txt",
        ".env",
        ".env_example",
    ]

    current = start_path.resolve()

    while current != current.parent:
        if any((current / marker).exists() for marker in markers):
            return current
        current = current.parent

    return start_path


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = find_project_root(CURRENT_FILE)

# Candidate env locations (priority order)
ENV_CANDIDATES = [
    PROJECT_ROOT / ".env",
    PROJECT_ROOT / "src" / ".env",
    CURRENT_FILE.parents[2] / ".env",  # fallback legacy layout
]


def load_env_file():
    """
    Load first existing .env file.
    """
    for env_path in ENV_CANDIDATES:
        if env_path.exists():
            load_dotenv(env_path)
            return env_path
    return None


LOADED_ENV_PATH = load_env_file()


# =========================================================
# MAIN SETTINGS CLASS
# =========================================================

class Settings(BaseSettings):
    """
    Global Application Settings.
    """

    # =====================================================
    # APP INFO
    # =====================================================
    APP_NAME: str = "AI Learning Platform Backend"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"


    # =====================================================
    # SECURITY
    # =====================================================
    SECRET_KEY: str = ""

    # =====================================================
    #DATABASE CONFIG
    # =====================================================
    DATABASE_URL:str

    # =====================================================
    # OPENAI CONFIG (Current Active LLM Provider)
    # =====================================================
    OPENAI_API_KEY: str | None = None
    OPENAI_API_BASE: str | None = None


    # =====================================================
    # DEFAULT LLM CONFIG
    # =====================================================
    DEFAULT_LLM_PROVIDER: str = "openai"
    DEFAULT_LLM_MODEL: str = "gpt-4o"

    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 1024
    DEFAULT_TIMEOUT: int = 60


    # =====================================================
    # CORS CONFIG (Frontend Future)
    # =====================================================
    CORS_ORIGINS: List[str] = ["*"]


    # =====================================================
    # GUARDRAIL CONFIG
    # =====================================================
    ENABLE_BANLIST_FILTER: bool = True
    BANNED_KEYWORDS: list[str] = [
        "illegal",
        "exploit",
        "bypass",
    ]

    # =====================================================
    # PYDANTIC SETTINGS CONFIG
    # =====================================================
    model_config = SettingsConfigDict(
        env_file=None,  # Disable pydantic's own env file loading
        case_sensitive=True,
        extra="ignore"
    )

# =========================================================
# GLOBAL SETTINGS INSTANCE
# =====================================================

settings = Settings()
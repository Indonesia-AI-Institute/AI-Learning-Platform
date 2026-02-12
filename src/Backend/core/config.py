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

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ConfigDict


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
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

# =========================================================
# GLOBAL SETTINGS INSTANCE
# =====================================================

settings = Settings()
import pytest
from pydantic import ValidationError

from backend.core.config import Settings

VALID_KWARGS = dict(
    SECRET_KEY="a-random-secret-key-that-is-at-least-32-chars",
    DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
    CORS_ORIGINS=["http://localhost:3000"],
)


def test_settings_construct_with_valid_values():
    s = Settings(**VALID_KWARGS)
    assert s.SECRET_KEY == VALID_KWARGS["SECRET_KEY"]
    assert s.CORS_ORIGINS == ["http://localhost:3000"]


def test_empty_secret_key_rejected():
    kwargs = {**VALID_KWARGS, "SECRET_KEY": ""}
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        Settings(**kwargs)


def test_short_secret_key_rejected():
    kwargs = {**VALID_KWARGS, "SECRET_KEY": "too-short"}
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        Settings(**kwargs)


def test_secret_key_31_chars_rejected():
    kwargs = {**VALID_KWARGS, "SECRET_KEY": "x" * 31}
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        Settings(**kwargs)


def test_secret_key_exactly_32_chars_is_accepted():
    kwargs = {**VALID_KWARGS, "SECRET_KEY": "x" * 32}
    s = Settings(**kwargs)
    assert s.SECRET_KEY == "x" * 32


def test_secret_key_well_over_32_chars_is_accepted():
    kwargs = {**VALID_KWARGS, "SECRET_KEY": "x" * 128}
    s = Settings(**kwargs)
    assert len(s.SECRET_KEY) == 128


def test_default_values_for_optional_settings():
    s = Settings(**VALID_KWARGS)
    assert s.APP_NAME == "AI Learning Platform Backend"
    assert s.ENVIRONMENT == "development"
    assert s.DEBUG is False
    assert s.HOST == "0.0.0.0"
    assert s.PORT == 8000
    assert s.DEFAULT_LLM_PROVIDER == "openai"
    assert s.ENABLE_STREAMING is True
    assert s.ENABLE_RAG is False
    assert s.ENABLE_BANLIST_FILTER is True
    assert s.BANNED_KEYWORDS == ["illegal", "exploit", "bypass"]
    assert s.LOG_LEVEL == "INFO"


def test_cors_origins_parses_json_array_from_env_string(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", '["https://a.example.com", "https://b.example.com"]')
    kwargs = {k: v for k, v in VALID_KWARGS.items() if k != "CORS_ORIGINS"}
    s = Settings(**kwargs)
    assert s.CORS_ORIGINS == ["https://a.example.com", "https://b.example.com"]


def test_field_names_are_case_sensitive(monkeypatch):
    # case_sensitive=True in model_config — a lowercase kwarg (or env var)
    # must not silently satisfy the uppercase field.
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    kwargs = {k: v for k, v in VALID_KWARGS.items() if k != "CORS_ORIGINS"}
    kwargs["cors_origins"] = ["http://localhost:3000"]
    with pytest.raises(ValidationError, match="CORS_ORIGINS"):
        Settings(**kwargs)


def test_cors_origins_is_required(monkeypatch):
    # conftest sets CORS_ORIGINS as a fallback env var so the app can import
    # at all; unset it here so a missing kwarg doesn't silently fall back to it.
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    kwargs = {k: v for k, v in VALID_KWARGS.items() if k != "CORS_ORIGINS"}
    with pytest.raises(ValidationError, match="CORS_ORIGINS"):
        Settings(**kwargs)


def test_database_url_is_required(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    kwargs = {k: v for k, v in VALID_KWARGS.items() if k != "DATABASE_URL"}
    with pytest.raises(ValidationError, match="DATABASE_URL"):
        Settings(**kwargs)

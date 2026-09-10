import pytest

from backend.core.config import settings
from backend.llm.services.llm_service import LLMService


@pytest.fixture
def service():
    return LLMService()


def test_banlist_check_blocks_when_enabled(service, monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_BANLIST_FILTER", True)
    monkeypatch.setattr(settings, "BANNED_KEYWORDS", ["illegal"])
    service.banlist_filter = service.banlist_filter.__class__(settings.BANNED_KEYWORDS)

    with pytest.raises(ValueError, match="banned keyword"):
        service._check_banlist("this is illegal")


def test_banlist_check_is_a_noop_when_disabled(service, monkeypatch):
    """
    Regression test: ENABLE_BANLIST_FILTER used to be defined in Settings
    but never actually read anywhere — the filter always ran regardless
    of the toggle. Turning it off must actually turn it off.
    """
    monkeypatch.setattr(settings, "ENABLE_BANLIST_FILTER", False)
    monkeypatch.setattr(settings, "BANNED_KEYWORDS", ["illegal"])
    service.banlist_filter = service.banlist_filter.__class__(settings.BANNED_KEYWORDS)

    service._check_banlist("this is illegal")  # must not raise

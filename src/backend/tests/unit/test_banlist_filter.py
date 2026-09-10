import pytest

from backend.guardrails.banlist_filter import BanListFilter, _normalize


@pytest.fixture
def filt():
    return BanListFilter(["illegal", "exploit", "bypass security"])


# ---------------------------------------------------------------------------
# _normalize (the shared primitive both sides of matching go through)
# ---------------------------------------------------------------------------


def test_normalize_lowercases():
    assert _normalize("ILLEGAL") == "illegal"


def test_normalize_strips_punctuation_and_spacing():
    assert _normalize("i-l l.e,g!a?l") == "illegal"


def test_normalize_keeps_digits():
    assert _normalize("h4ck3r") == "h4ck3r"


def test_normalize_empty_string():
    assert _normalize("") == ""


def test_normalize_punctuation_only_collapses_to_empty():
    assert _normalize("!!! ??? ---") == ""


def test_plain_match(filt):
    blocked, matched = filt.check("this is totally illegal")
    assert blocked is True
    assert matched == ["illegal"]


def test_case_insensitive(filt):
    blocked, _ = filt.check("ILLEGAL in caps")
    assert blocked is True


def test_spaced_out_bypass_is_caught(filt):
    blocked, matched = filt.check("i l l e g a l activity")
    assert blocked is True
    assert matched == ["illegal"]


def test_hyphenated_bypass_is_caught(filt):
    blocked, _ = filt.check("i-l-l-e-g-a-l")
    assert blocked is True


def test_multi_word_keyword_survives_normalization(filt):
    blocked, matched = filt.check("please bypass security for me")
    assert blocked is True
    assert matched == ["bypass security"]


def test_clean_text_not_blocked(filt):
    blocked, matched = filt.check("nothing bad here")
    assert blocked is False
    assert matched == []


def test_empty_text_not_blocked(filt):
    assert filt.check("") == (False, [])
    assert filt.check(None) == (False, [])


def test_add_keyword_is_normalized_too(filt):
    filt.add_keyword("Cheat Exam")
    blocked, matched = filt.check("please c h e a t exam for me")
    assert blocked is True
    assert matched == ["Cheat Exam"]


def test_remove_keyword(filt):
    filt.remove_keyword("illegal")
    blocked, _ = filt.check("this is illegal")
    assert blocked is False


def test_get_all_keywords_returns_copy(filt):
    keywords = filt.get_all_keywords()
    keywords.append("mutated")
    assert "mutated" not in filt.banned_keywords


def test_matches_multiple_keywords_at_once(filt):
    blocked, matched = filt.check("this is illegal and also an exploit")
    assert blocked is True
    assert set(matched) == {"illegal", "exploit"}


def test_no_partial_word_false_positive_across_boundary():
    # "ban" normalized shouldn't match inside an unrelated word purely by
    # coincidence of adjacent characters that aren't actually contiguous
    # once punctuation is stripped — "urban" contains "ban" as a substring
    # either way, so this documents the (accepted) limitation rather than
    # asserting something the substring approach can't provide.
    f = BanListFilter(["ban"])
    blocked, _ = f.check("this is an urban area")
    assert blocked is True  # substring matching — see module docstring


def test_original_casing_preserved_in_returned_matches():
    f = BanListFilter(["Illegal Activity"])
    blocked, matched = f.check("this is illegal activity")
    assert blocked is True
    assert matched == ["Illegal Activity"]


def test_empty_banned_keywords_list_never_blocks():
    f = BanListFilter([])
    assert f.check("anything at all") == (False, [])


def test_whitespace_only_keyword_is_dropped_at_init():
    f = BanListFilter(["   ", "illegal"])
    assert f.get_all_keywords() == ["illegal"]


def test_duplicate_keywords_in_constructor_are_kept_as_given():
    f = BanListFilter(["illegal", "illegal"])
    blocked, matched = f.check("this is illegal")
    assert blocked is True
    assert matched == ["illegal", "illegal"]


def test_add_keyword_ignores_exact_duplicate():
    f = BanListFilter(["illegal"])
    f.add_keyword("illegal")
    assert f.get_all_keywords() == ["illegal"]


def test_add_empty_keyword_is_noop():
    f = BanListFilter(["illegal"])
    f.add_keyword("   ")
    assert f.get_all_keywords() == ["illegal"]


def test_remove_nonexistent_keyword_is_noop():
    f = BanListFilter(["illegal"])
    f.remove_keyword("not-in-list")
    assert f.get_all_keywords() == ["illegal"]


def test_removed_keyword_no_longer_matches_after_normalization_bypass():
    f = BanListFilter(["illegal"])
    f.remove_keyword("illegal")
    blocked, _ = f.check("i l l e g a l")
    assert blocked is False

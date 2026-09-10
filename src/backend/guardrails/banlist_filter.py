"""
Simple keyword banlist guardrail.

This is defense-in-depth, not a real content-safety guarantee: normalized
substring matching still can't catch synonyms, other languages, or
indirect phrasing. If moderation quality actually matters, that needs a
classifier, not a keyword list.
"""

import re
import unicodedata
from typing import List, Tuple


def _normalize(text: str) -> str:
    """Unicode-normalize, lowercase, and collapse everything but letters
    and digits — catches basic spacing/punctuation evasion like "i l l e
    g a l" or "i-l-l-e-g-a-l", which plain substring matching would miss."""
    text = unicodedata.normalize("NFKC", text).lower()
    return re.sub(r"[^a-z0-9]+", "", text)


class BanListFilter:
    """
    Simple banlist keyword filter.

    Usage:
        filter = BanListFilter(["cheat exam", "joki tugas"])
        is_blocked, matched = filter.check("tolong cheat exam saya")
    """

    def __init__(self, banned_keywords: List[str]):
        self.banned_keywords = [
            keyword.strip()
            for keyword in banned_keywords
            if keyword.strip()
        ]
        self._normalized_keywords = [
            (keyword, _normalize(keyword))
            for keyword in self.banned_keywords
        ]

    def check(self, text: str) -> Tuple[bool, List[str]]:
        """
        Check apakah text mengandung banned keyword.

        Returns
        -------
        Tuple[bool, List[str]]
            (is_blocked, matched_keywords)
        """

        if not text:
            return False, []

        normalized_text = _normalize(text)

        matched_keywords = [
            keyword
            for keyword, normalized_keyword in self._normalized_keywords
            if normalized_keyword and normalized_keyword in normalized_text
        ]

        return len(matched_keywords) > 0, matched_keywords

    def add_keyword(self, keyword: str):
        """Add keyword ke banlist runtime."""
        keyword = keyword.strip()
        if keyword and keyword not in self.banned_keywords:
            self.banned_keywords.append(keyword)
            self._normalized_keywords.append((keyword, _normalize(keyword)))

    def remove_keyword(self, keyword: str):
        """Remove keyword dari banlist runtime."""
        keyword = keyword.strip()
        if keyword in self.banned_keywords:
            self.banned_keywords.remove(keyword)
            self._normalized_keywords = [
                (k, nk) for k, nk in self._normalized_keywords if k != keyword
            ]

    def get_all_keywords(self) -> List[str]:
        """Return semua banned keywords."""
        return self.banned_keywords.copy()

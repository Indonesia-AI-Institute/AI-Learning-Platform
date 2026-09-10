"""
Simple keyword banlist guardrail (case-insensitive exact keyword match).
"""

from typing import List, Tuple


class BanListFilter:
    """
    Simple banlist keyword filter.

    Usage:
        filter = BanListFilter(["cheat exam", "joki tugas"])
        is_blocked, matched = filter.check("tolong cheat exam saya")
    """

    def __init__(self, banned_keywords: List[str]):
        """
        Parameters
        ----------
        banned_keywords : List[str]
            List keyword yang akan diblokir.
        """

        # Normalize keyword → lowercase + strip whitespace
        self.banned_keywords = [
            keyword.lower().strip()
            for keyword in banned_keywords
            if keyword.strip()
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

        text_lower = text.lower()

        matched_keywords = [
            keyword
            for keyword in self.banned_keywords
            if keyword in text_lower
        ]

        return len(matched_keywords) > 0, matched_keywords

    def add_keyword(self, keyword: str):
        """Add keyword ke banlist runtime."""
        keyword = keyword.lower().strip()
        if keyword and keyword not in self.banned_keywords:
            self.banned_keywords.append(keyword)

    def remove_keyword(self, keyword: str):
        """Remove keyword dari banlist runtime."""
        keyword = keyword.lower().strip()
        if keyword in self.banned_keywords:
            self.banned_keywords.remove(keyword)

    def get_all_keywords(self) -> List[str]:
        """Return semua banned keywords."""
        return self.banned_keywords.copy()
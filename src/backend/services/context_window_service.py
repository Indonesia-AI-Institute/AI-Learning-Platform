from typing import List, Dict

class ContextWindowService:
    """
    Responsible for trimming chat history to fit model context window.
    """

    def __init__(
        self,
        max_tokens: int = 12000,
        reserve_tokens: int = 2000,
    ):
        """
        max_tokens:
            max context window of model

        reserve_tokens:
            reserved tokens for assistant response
        """

        self.max_tokens = max_tokens
        self.reserve_tokens = reserve_tokens

    # =================================
    # SIMPLE TOKEN ESTIMATION
    # =================================

    def estimate_tokens(self, text: str) -> int:
        """
        Rough token estimation.
        1 token ≈ 4 characters
        """

        return max(1, len(text) // 4)

    # =================================
    # TRIM CONTEXT
    # =================================

    def trim_messages(
        self,
        messages: List[Dict[str, str]],
    ) -> List[Dict[str, str]]:

        max_context_tokens = self.max_tokens - self.reserve_tokens

        total_tokens = 0
        trimmed_messages: List[Dict[str, str]] = []

        # iterate from newest
        for msg in reversed(messages):

            tokens = self.estimate_tokens(msg["content"])

            if total_tokens + tokens > max_context_tokens:
                break

            trimmed_messages.append(msg)
            total_tokens += tokens

        trimmed_messages.reverse()

        return trimmed_messages
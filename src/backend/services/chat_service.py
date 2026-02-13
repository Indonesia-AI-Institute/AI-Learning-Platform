"""
chat_service.py
===============

Business service untuk chatbot orchestration.

Tanggung jawab:
- Handle chat request dari API layer
- Normalisasi input message
- Call LLM Service
- Future hook untuk:
    - Task logging
    - Prompt scoring
    - Analytics

Saat ini fokus:
✔ Stateless chat
✔ Raw prompt passthrough
✔ SSE streaming ready
✔ Multi session ready (future DB)

Tidak termasuk:
❌ Database
❌ Task persistence
❌ Prompt scoring automation
"""

from typing import List, Dict, Any, AsyncGenerator

from llm.service.llm_service import LLMService


class ChatService:
    """
    Main business service untuk Chatbot.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    # =====================================================
    # INTERNAL MESSAGE BUILDER
    # =====================================================

    def _build_messages(
        self,
        user_prompt: str,
        system_prompt: str | None = None,
        chat_history: List[Dict[str, str]] | None = None,
    ) -> List[Dict[str, str]]:
        """
        Convert input menjadi OpenAI-compatible messages format.
        """

        messages: List[Dict[str, str]] = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt,
            })

        if chat_history:
            messages.extend(chat_history)

        messages.append({
            "role": "user",
            "content": user_prompt,
        })

        return messages

    def _normalize_llm_response(
        self,
        resp: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Normalize provider response → domain response contract.

        Supports future multi-provider mapping.
        """

        # --- Content fallback chain (future proof) ---
        content = (
            resp.get("content")
            or resp.get("text")
            or resp.get("completion")
            or ""
        )

        # --- Optional Safety Guard ---
        if not content:
            raise ValueError("LLM returned empty content")

        return {
            "response_text": content,
            "usage": resp.get("usage"),
            "model": resp.get("model")
            # Future ready:
            # "provider": resp.get("provider")
            # "latency_ms": resp.get("latency")
        }

    # =====================================================
    # NON STREAM CHAT
    # =====================================================

    async def chat(
        self,
        user_prompt: str,
        system_prompt: str | None = None,
        chat_history: List[Dict[str, str]] | None = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Non streaming chat response.
        """

        messages = self._build_messages(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            chat_history=chat_history,
        )

        response = await self.llm_service.generate(
            messages=messages,
            **kwargs,
        )

        return self._normalize_llm_response(response)

    # =====================================================
    # STREAM CHAT (MAIN CHATBOT PATH)
    # =====================================================

    async def stream_chat(
        self,
        user_prompt: str,
        system_prompt: str | None = None,
        chat_history: List[Dict[str, str]] | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """
        Streaming chat response untuk SSE endpoint.
        """

        messages = self._build_messages(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            chat_history=chat_history,
        )

        async for token in self.llm_service.stream_generate(
            messages=messages,
            **kwargs,
        ):
            yield token
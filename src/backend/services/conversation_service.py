"""
conversation_service.py
===============
"""

from typing import Dict, Any, AsyncGenerator
from uuid import UUID
import time

from src.backend.models.user import User

from src.backend.services.session_service import SessionService
from src.backend.services.chat_history_service import ChatHistoryService
from src.backend.services.chat_service import ChatService


class ConversationService:
    """
    AI Conversation Orchestration Layer.

    Responsibilities
    ----------------
    - Validate session access
    - Persist user message
    - Build LLM context
    - Stream/generate AI response
    - Persist assistant response lifecycle
    """

    def __init__(
        self,
        session_service: SessionService,
        history_service: ChatHistoryService,
        chat_service: ChatService,
    ):
        self.session_service = session_service
        self.history_service = history_service
        self.chat_service = chat_service

    # =====================================================
    # NON STREAM RESPONSE
    # =====================================================

    async def send_message(
        self,
        current_user: User,
        session_id: UUID,
        agent_type: str,
        content: str,
        system_prompt: str | None = None,
        **agent_kwargs: Any,
    ) -> Dict[str, Any]:

        # 1️⃣ Validate session
        db_session = await self.session_service.get_session_detail(
            current_user=current_user,
            session_id=session_id,
        )

        if not db_session.is_active:
            raise ValueError("Session is not active.")

        # 2️⃣ Save USER message
        await self.history_service.add_user_message(
            session_id=session_id,
            user_id=current_user.id,
            content=content,
        )

        # 3️⃣ Build context
        messages = await self.history_service.build_llm_context(
            session_id=session_id,
            include_system_prompt=system_prompt,
        )

        start_time = time.time()

        # 4️⃣ Call AI
        ai_response = await self.chat_service.generate(
            agent_type=agent_type,
            messages=messages,
            **agent_kwargs,
        )

        latency = int((time.time() - start_time) * 1000)

        assistant_content = ai_response.get("content")

        usage = ai_response.get("usage", {})

        # 5️⃣ Save assistant response
        assistant_message = await self.history_service.create_assistant_message(
            session_id=session_id,
            model_name=ai_response.get("model"),
            provider_name=ai_response.get("provider"),
        )

        await self.history_service.finalize_assistant_message(
            message_id=assistant_message.id,
            content=assistant_content,
            input_tokens=usage.get("prompt_tokens") or 0,
            output_tokens=usage.get("completion_tokens") or 0,
            latency_ms=latency,
            metadata=ai_response.get("metadata"),
        )

        return ai_response

    # =====================================================
    # STREAM RESPONSE
    # =====================================================

    async def stream_message(
        self,
        current_user: User,
        session_id: UUID,
        agent_type: str,
        content: str,
        system_prompt: str | None = None,
        **agent_kwargs: Any,
    ) -> AsyncGenerator[str, None]:

        # 1️⃣ Validate session
        db_session = await self.session_service.get_session_detail(
            current_user=current_user,
            session_id=session_id,
        )

        if not db_session.is_active:
            raise ValueError("Session is not active.")

        # 2️⃣ Save USER message
        await self.history_service.add_user_message(
            session_id=session_id,
            user_id=current_user.id,
            content=content,
        )

        # 3️⃣ Build context
        messages = await self.history_service.build_llm_context(
            session_id=session_id,
            include_system_prompt=system_prompt,
        )

        # 4️⃣ Create assistant message
        assistant_message = await self.history_service.create_assistant_message(
            session_id=session_id,
            model_name=None,
            provider_name=None,
        )

        start_time = time.time()

        full_response = ""
        token_buffer = ""

        usage = {}
        finish_reason = None
        model_name = None
        provider_name = None

        BUFFER_SIZE = 20

        # 5️⃣ Stream AI
        async for event in self.chat_service.stream_generate(
            agent_type=agent_type,
            messages=messages,
            **agent_kwargs,
        ):

            if event["type"] == "token":

                token = event["content"]

                full_response += token
                token_buffer += token

                yield token

                # 🔥 incremental save
                if len(token_buffer) >= BUFFER_SIZE:

                    await self.history_service.update_streaming_content(
                        message_id=assistant_message.id,
                        partial_content=token_buffer,
                    )

                    token_buffer = ""

            elif event["type"] == "start":

                model_name = event.get("model")
                provider_name = event.get("provider")

                await self.history_service.set_model_provider(
                    message_id=assistant_message.id,
                    model_name=model_name,
                    provider_name=provider_name,
                )

            elif event["type"] == "done":

                usage = event.get("usage", {})
                finish_reason = event.get("finish_reason")

        # save remaining buffer
        if token_buffer:
            await self.history_service.update_streaming_content(
                message_id=assistant_message.id,
                partial_content=token_buffer,
            )

        latency = int((time.time() - start_time) * 1000)

        # 6️⃣ Finalize message
        await self.history_service.finalize_assistant_message(
            message_id=assistant_message.id,
            content=full_response,
            input_tokens=usage.get("prompt_tokens") or 0,
            output_tokens=usage.get("completion_tokens") or 0,
            latency_ms=latency,
            metadata={
                "finish_reason": finish_reason
            },
        )
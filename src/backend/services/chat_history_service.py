from typing import List, Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.services.context_window_service import ContextWindowService
from backend.models.chat_history import ChatHistory, MessageRole, MessageStatus
from backend.repositories.chat_history_repository import ChatHistoryRepository


class ChatHistoryService:
    """
    Chat history persistence layer.

    Responsibilities:
    - Store messages
    - Retrieve session history
    - Build LLM context
    - Handle assistant streaming lifecycle
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.history_repo = ChatHistoryRepository(db)
        self.context_window_service = ContextWindowService()

    async def _get_next_index(self, session_id: UUID) -> int:
        # NOTE: with_for_update() is NOT allowed with aggregate functions in PostgreSQL.
        # Using get_last_message_index() from repository which uses plain max() query.
        last_index = await self.history_repo.get_last_message_index(session_id)
        return last_index + 1

    async def set_model_provider(
        self,
        message_id: UUID,
        model_name: str,
        provider_name: str,
    ):
        await self.history_repo.update_message(
            message_id=message_id,
            model_name=model_name,
            provider_name=provider_name,
        )

    async def add_user_message(
        self,
        session_id: UUID,
        user_id: UUID,
        content: str,
    ) -> ChatHistory:

        message_index = await self._get_next_index(session_id)

        new_history = ChatHistory(
            session_id=session_id,
            role=MessageRole.USER,
            content=content,
            user_id=user_id,
            message_index=message_index,
            status=MessageStatus.COMPLETED,
        )

        return await self.history_repo.create_message(new_history)

    async def create_assistant_message(
        self,
        session_id: UUID,
        model_name: str,
        provider_name: str,
    ) -> ChatHistory:

        message_index = await self._get_next_index(session_id)

        new_history = ChatHistory(
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content="",
            user_id=None,
            message_index=message_index,
            status=MessageStatus.STREAMING,
            model_name=model_name,
            provider_name=provider_name,
        )

        return await self.history_repo.create_message(new_history)

    async def finalize_assistant_message(
        self,
        message_id: UUID,
        content: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        latency_ms: int = 0,
        metadata: Optional[dict] = None,
    ) -> ChatHistory:

        return await self.history_repo.update_message(
            message_id=message_id,
            content=content,
            status=MessageStatus.COMPLETED,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            message_metadata=metadata,
        )

    async def get_session_history(
        self,
        session_id: UUID,
    ) -> List[ChatHistory]:

        stmt = (
            select(ChatHistory)
            .where(
                ChatHistory.session_id == session_id,
                ChatHistory.status != MessageStatus.ABORTED,
            )
            .order_by(ChatHistory.message_index.asc())
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def build_llm_context(
        self,
        session_id: UUID,
        include_system_prompt: Optional[str] = None,
    ) -> List[Dict[str, str]]:

        history = await self.get_session_history(session_id)

        messages: List[Dict[str, str]] = []

        if include_system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": include_system_prompt,
                }
            )

        for msg in history:
            messages.append(
                {
                    "role": msg.role.value,
                    "content": msg.content,
                }
            )

        messages = self.context_window_service.trim_messages(messages)
        return messages

    async def get_session_messages(
        self,
        session_id: UUID,
        limit: int = 50,
        cursor: Optional[int] = None,
    ) -> List[ChatHistory]:

        stmt = select(ChatHistory).where(
            ChatHistory.session_id == session_id
        )

        if cursor:
            stmt = stmt.where(ChatHistory.message_index > cursor)

        stmt = stmt.order_by(ChatHistory.message_index.asc()).limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_streaming_content(
        self,
        message_id: UUID,
        partial_content: str,
    ):
        stmt = select(ChatHistory).where(ChatHistory.id == message_id)
        result = await self.db.execute(stmt)
        message = result.scalar_one_or_none()

        if not message:
            return

        await self.history_repo.update_message(
            message_id=message_id,
            content=message.content + partial_content,
        )
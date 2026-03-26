from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.chat_history import ChatHistory


class ChatHistoryRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # =========================
    # CREATE MESSAGE
    # =========================
    async def create_message(self, message: ChatHistory) -> ChatHistory:
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    # =========================
    # GET SESSION HISTORY
    # =========================
    async def get_session_messages(
        self,
        session_id: UUID
    ) -> List[ChatHistory]:

        result = await self.db.execute(
            select(ChatHistory)
            .where(ChatHistory.session_id == session_id)
            .order_by(ChatHistory.message_index.asc())
        )

        return result.scalars().all()

    # =========================
    # GET LAST MESSAGE INDEX
    # =========================
    async def get_last_message_index(
        self,
        session_id: UUID
    ) -> int:

        result = await self.db.execute(
            select(func.max(ChatHistory.message_index))
            .where(ChatHistory.session_id == session_id)
        )

        last_index = result.scalar()

        if last_index is None:
            return 0

        return last_index

    # =========================
    # UPDATE MESSAGE
    # =========================
    async def update_message(
        self,
        message_id: UUID,
        **kwargs
    ) -> Optional[ChatHistory]:

        result = await self.db.execute(
            select(ChatHistory).where(ChatHistory.id == message_id)
        )

        message = result.scalar_one_or_none()

        if not message:
            return None

        for key, value in kwargs.items():
            setattr(message, key, value)

        await self.db.commit()
        await self.db.refresh(message)

        return message
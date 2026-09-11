from typing import Optional
from uuid import UUID

from backend.models.chat_history import ChatHistory
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class ChatHistoryRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_message(self, message: ChatHistory) -> ChatHistory:
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

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
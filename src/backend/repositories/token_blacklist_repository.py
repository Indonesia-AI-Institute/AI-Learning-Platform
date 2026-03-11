"""
token_blacklist_repository.py
=============================

Store blacklisted JWT tokens.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.backend.models.token_blacklist import TokenBlacklist


class TokenBlacklistRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_token(self, token: str):
        entry = TokenBlacklist(token=token)
        self.db.add(entry)
        await self.db.commit()

    async def is_blacklisted(self, token: str) -> bool:
        stmt = select(TokenBlacklist).where(TokenBlacklist.token == token)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
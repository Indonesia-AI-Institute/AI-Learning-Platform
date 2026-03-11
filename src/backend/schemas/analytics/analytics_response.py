"""
schemas/analytics/analytics_response.py
=======================================
"""

from datetime import datetime
from pydantic import BaseModel


class AnalyticsResponse(BaseModel):
    total_sessions: int
    total_messages: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int
    last_active: datetime | None
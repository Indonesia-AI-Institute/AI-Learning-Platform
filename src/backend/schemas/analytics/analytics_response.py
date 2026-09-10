from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AnalyticsResponse(BaseModel):
    total_sessions: int
    total_prompts: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int
    avg_prompt_length: float
    total_duration_seconds: int
    last_active: Optional[datetime]
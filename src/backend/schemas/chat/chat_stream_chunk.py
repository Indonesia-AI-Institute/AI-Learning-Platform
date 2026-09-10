"""
Schema untuk streaming chunk data via SSE.

Digunakan untuk:
- Streaming token response dari LLM
- Standardisasi format SSE message

Saat ini fokus:
✔ Token streaming
✔ Done event
✔ Error event

Future Ready:
- Usage token summary
- Reasoning trace
- Latency metrics
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field, model_validator


StreamEventType = Literal[
    "token",
    "done",
    "error"
]


class ChatStreamChunk(BaseModel):
    """
    Standard SSE chunk format.
    """

    event: StreamEventType = Field(
        ...,
        description="Jenis streaming event"
    )

    data: Optional[str] = Field(
        None,
        description="Isi token / message streaming"
    )

    error_message: Optional[str] = Field(
        None,
        description="Error message jika event = error"
    )

    @model_validator(mode="after")
    def validate_event_payload(self):
        """
        Ensure correct payload based on event type.
        """

        if self.event == "token" and not self.data:
            raise ValueError("Token event must contain data")

        if self.event == "error" and not self.error_message:
            raise ValueError("Error event must contain error_message")

        if self.event == "done":
            # done should not carry token or error
            self.data = None
            self.error_message = None

        return self

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "event": "token",
                    "data": "Artificial "
                },
                {
                    "event": "token",
                    "data": "Intelligence "
                },
                {
                    "event": "done"
                },
                {
                    "event": "error",
                    "error_message": "LLM timeout"
                }
            ]
        }
    }

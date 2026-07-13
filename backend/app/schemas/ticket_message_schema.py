import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.ticket_schema import TicketUserSummary


class TicketMessageCreate(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=5000,
        examples=[
            "I tested another power cable, but the computer still does not turn on."
        ],
    )

    is_internal: bool = Field(
        default=False,
        description="Internal notes are visible only to support members.",
    )

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        normalized_content = value.strip()

        if not normalized_content:
            raise ValueError("Message content cannot be empty")

        return normalized_content


class TicketMessageResponse(BaseModel):
    id: uuid.UUID
    ticket_id: uuid.UUID
    author_id: uuid.UUID | None
    content: str
    is_internal: bool
    author: TicketUserSummary | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.ticket_model import TicketPriority, TicketStatus


class TicketCreate(BaseModel):
    title: str = Field(
        min_length=5,
        max_length=160,
        examples=["Computer does not turn on"],
    )

    description: str = Field(
        min_length=10,
        max_length=5000,
        examples=[
            "The computer does not turn on after pressing the power button."
        ],
    )

    priority: TicketPriority = Field(
        default=TicketPriority.MEDIUM,
        examples=[TicketPriority.MEDIUM],
    )

    @field_validator("title", "description")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        normalized_value = " ".join(value.split())

        if not normalized_value:
            raise ValueError("Field cannot be empty")

        return normalized_value


class TicketAssign(BaseModel):
    technician_id: uuid.UUID | None = Field(
        default=None,
        description=(
            "Technician ID. Technicians may omit this field to assign "
            "the ticket to themselves."
        ),
    )


class TicketStatusUpdate(BaseModel):
    status: TicketStatus


class TicketPriorityUpdate(BaseModel):
    priority: TicketPriority


class TicketUserSummary(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class TicketResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    status: TicketStatus
    priority: TicketPriority

    requester_id: uuid.UUID
    assigned_to_id: uuid.UUID | None

    requester: TicketUserSummary
    assigned_to: TicketUserSummary | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
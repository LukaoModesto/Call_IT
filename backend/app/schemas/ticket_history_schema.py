import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.ticket_history_model import TicketHistoryAction
from app.schemas.ticket_schema import TicketUserSummary


class TicketHistoryResponse(BaseModel):
    id: uuid.UUID
    ticket_id: uuid.UUID
    actor_id: uuid.UUID | None
    action: TicketHistoryAction
    old_value: str | None
    new_value: str | None
    actor: TicketUserSummary | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
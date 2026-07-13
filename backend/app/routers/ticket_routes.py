import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_any_user
from app.database.session import get_db
from app.models.ticket_model import Ticket
from app.models.user_model import User
from app.schemas.ticket_schema import TicketCreate, TicketResponse
from app.services.ticket_service import (
    create_ticket,
    get_ticket_by_id,
    get_tickets_for_user,
    user_can_view_ticket,
)


router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
)


@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def open_ticket(
    ticket_data: TicketCreate,
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_any_user),
) -> Ticket:
    return create_ticket(
        database=database,
        ticket_data=ticket_data,
        requester=current_user,
    )


@router.get(
    "",
    response_model=list[TicketResponse],
)
def list_tickets(
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_any_user),
) -> list[Ticket]:
    return get_tickets_for_user(
        database=database,
        current_user=current_user,
    )


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
)
def get_ticket(
    ticket_id: uuid.UUID,
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_any_user),
) -> Ticket:
    ticket = get_ticket_by_id(
        database=database,
        ticket_id=ticket_id,
    )

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    if not user_can_view_ticket(
        current_user=current_user,
        ticket=ticket,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this ticket",
        )

    return ticket
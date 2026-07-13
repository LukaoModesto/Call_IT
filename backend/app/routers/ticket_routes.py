import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_any_user,
    get_current_support_member,
)
from app.database.session import get_db
from app.models.ticket_model import Ticket
from app.models.user_model import User, UserRole
from app.schemas.ticket_schema import (
    TicketAssign,
    TicketCreate,
    TicketPriorityUpdate,
    TicketResponse,
    TicketStatusUpdate,
)
from app.services.ticket_service import (
    assign_ticket,
    create_ticket,
    get_ticket_by_id,
    get_ticket_history,
    get_tickets_for_user,
    update_ticket_priority,
    update_ticket_status,
    user_can_view_ticket,
)
from app.services.user_service import get_support_user_by_id
from app.schemas.ticket_history_schema import TicketHistoryResponse

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
)


def get_existing_ticket(
    ticket_id: uuid.UUID,
    database: Session,
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

    return ticket


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
    "/{ticket_id}/history",
    response_model=list[TicketHistoryResponse],
)
def list_ticket_history(
    ticket_id: uuid.UUID,
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_any_user),
):
    ticket = get_existing_ticket(
        ticket_id=ticket_id,
        database=database,
    )

    if not user_can_view_ticket(
        current_user=current_user,
        ticket=ticket,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this ticket history",
        )

    return get_ticket_history(
        database=database,
        ticket_id=ticket.id,
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
    ticket = get_existing_ticket(
        ticket_id=ticket_id,
        database=database,
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


@router.patch(
    "/{ticket_id}/assign",
    response_model=TicketResponse,
)
def assign_ticket_to_technician(
    ticket_id: uuid.UUID,
    assignment_data: TicketAssign,
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_support_member),
) -> Ticket:
    ticket = get_existing_ticket(
        ticket_id=ticket_id,
        database=database,
    )

    technician: User | None

    if current_user.role == UserRole.TECHNICIAN:
        if (
            assignment_data.technician_id is not None
            and assignment_data.technician_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Technicians can only assign tickets to themselves",
            )

        technician = current_user

    else:
        if assignment_data.technician_id is None:
            technician = None
        else:
            technician = get_support_user_by_id(
                database=database,
                user_id=assignment_data.technician_id,
            )

            if technician is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Active technician or administrator not found",
                )

    return assign_ticket(
        database=database,
        ticket=ticket,
        technician=technician,
        actor=current_user,
    )


@router.patch(
    "/{ticket_id}/status",
    response_model=TicketResponse,
)
def change_ticket_status(
    ticket_id: uuid.UUID,
    status_data: TicketStatusUpdate,
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_support_member),
) -> Ticket:
    ticket = get_existing_ticket(
        ticket_id=ticket_id,
        database=database,
    )

    if (
        current_user.role == UserRole.TECHNICIAN
        and ticket.assigned_to_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Technicians can only update tickets assigned to them",
        )

    return update_ticket_status(
        database=database,
        ticket=ticket,
        new_status=status_data.status,
        actor=current_user,
    )


@router.patch(
    "/{ticket_id}/priority",
    response_model=TicketResponse,
)
def change_ticket_priority(
    ticket_id: uuid.UUID,
    priority_data: TicketPriorityUpdate,
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_support_member),
) -> Ticket:
    ticket = get_existing_ticket(
        ticket_id=ticket_id,
        database=database,
    )

    if (
        current_user.role == UserRole.TECHNICIAN
        and ticket.assigned_to_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Technicians can only update tickets assigned to them",
        )

    return update_ticket_priority(
        database=database,
        ticket=ticket,
        new_priority=priority_data.priority,
        actor=current_user,
    )
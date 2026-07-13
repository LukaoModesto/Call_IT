import uuid

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload

from app.models.ticket_model import Ticket
from app.models.user_model import User, UserRole
from app.schemas.ticket_schema import TicketCreate


def create_ticket(
    database: Session,
    ticket_data: TicketCreate,
    requester: User,
) -> Ticket:
    ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        priority=ticket_data.priority,
        requester_id=requester.id,
    )

    database.add(ticket)
    database.commit()
    database.refresh(ticket)

    return get_ticket_by_id(
        database=database,
        ticket_id=ticket.id,
    )


def get_ticket_by_id(
    database: Session,
    ticket_id: uuid.UUID,
) -> Ticket | None:
    statement = (
        select(Ticket)
        .options(
            joinedload(Ticket.requester),
            joinedload(Ticket.assigned_to),
        )
        .where(Ticket.id == ticket_id)
    )

    return database.scalar(statement)


def get_tickets_for_user(
    database: Session,
    current_user: User,
) -> list[Ticket]:
    statement: Select[tuple[Ticket]] = (
        select(Ticket)
        .options(
            joinedload(Ticket.requester),
            joinedload(Ticket.assigned_to),
        )
        .order_by(Ticket.created_at.desc())
    )

    if current_user.role == UserRole.REQUESTER:
        statement = statement.where(
            Ticket.requester_id == current_user.id,
        )

    return list(database.scalars(statement).all())


def user_can_view_ticket(
    current_user: User,
    ticket: Ticket,
) -> bool:
    if current_user.role in {
        UserRole.TECHNICIAN,
        UserRole.ADMINISTRATOR,
    }:
        return True

    return ticket.requester_id == current_user.id
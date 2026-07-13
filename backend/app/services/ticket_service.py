import uuid

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload

from app.models.ticket_history_model import (
    TicketHistory,
    TicketHistoryAction,
)
from app.models.ticket_model import (
    Ticket,
    TicketPriority,
    TicketStatus,
)
from app.models.user_model import User, UserRole
from app.models.ticket_message_model import TicketMessage
from app.schemas.ticket_schema import TicketCreate



def add_ticket_history(
    database: Session,
    ticket_id: uuid.UUID,
    actor_id: uuid.UUID | None,
    action: TicketHistoryAction,
    old_value: str | None = None,
    new_value: str | None = None,
) -> TicketHistory:
    history_entry = TicketHistory(
        ticket_id=ticket_id,
        actor_id=actor_id,
        action=action,
        old_value=old_value,
        new_value=new_value,
    )

    database.add(history_entry)

    return history_entry


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
    database.flush()

    add_ticket_history(
        database=database,
        ticket_id=ticket.id,
        actor_id=requester.id,
        action=TicketHistoryAction.CREATED,
        new_value=TicketStatus.OPEN.value,
    )

    database.commit()

    created_ticket = get_ticket_by_id(
        database=database,
        ticket_id=ticket.id,
    )

    if created_ticket is None:
        raise RuntimeError("Ticket could not be retrieved after creation")

    return created_ticket


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


def get_ticket_history(
    database: Session,
    ticket_id: uuid.UUID,
) -> list[TicketHistory]:
    statement = (
        select(TicketHistory)
        .options(
            joinedload(TicketHistory.actor),
        )
        .where(TicketHistory.ticket_id == ticket_id)
        .order_by(TicketHistory.created_at.asc())
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


def assign_ticket(
    database: Session,
    ticket: Ticket,
    technician: User | None,
    actor: User,
) -> Ticket:
    previous_technician_id = ticket.assigned_to_id
    new_technician_id = technician.id if technician is not None else None

    if previous_technician_id == new_technician_id:
        current_ticket = get_ticket_by_id(
            database=database,
            ticket_id=ticket.id,
        )

        if current_ticket is None:
            raise RuntimeError("Ticket could not be retrieved")

        return current_ticket

    ticket.assigned_to_id = new_technician_id

    action = (
        TicketHistoryAction.ASSIGNED
        if technician is not None
        else TicketHistoryAction.UNASSIGNED
    )

    add_ticket_history(
        database=database,
        ticket_id=ticket.id,
        actor_id=actor.id,
        action=action,
        old_value=(
            str(previous_technician_id)
            if previous_technician_id is not None
            else None
        ),
        new_value=(
            str(new_technician_id)
            if new_technician_id is not None
            else None
        ),
    )

    if technician is not None and ticket.status == TicketStatus.OPEN:
        previous_status = ticket.status
        ticket.status = TicketStatus.IN_TRIAGE

        add_ticket_history(
            database=database,
            ticket_id=ticket.id,
            actor_id=actor.id,
            action=TicketHistoryAction.STATUS_CHANGED,
            old_value=previous_status.value,
            new_value=TicketStatus.IN_TRIAGE.value,
        )

    database.commit()

    updated_ticket = get_ticket_by_id(
        database=database,
        ticket_id=ticket.id,
    )

    if updated_ticket is None:
        raise RuntimeError("Ticket could not be retrieved after assignment")

    return updated_ticket


def update_ticket_status(
    database: Session,
    ticket: Ticket,
    new_status: TicketStatus,
    actor: User,
) -> Ticket:
    previous_status = ticket.status

    if previous_status == new_status:
        return ticket

    ticket.status = new_status

    add_ticket_history(
        database=database,
        ticket_id=ticket.id,
        actor_id=actor.id,
        action=TicketHistoryAction.STATUS_CHANGED,
        old_value=previous_status.value,
        new_value=new_status.value,
    )

    database.commit()

    updated_ticket = get_ticket_by_id(
        database=database,
        ticket_id=ticket.id,
    )

    if updated_ticket is None:
        raise RuntimeError("Ticket could not be retrieved after status update")

    return updated_ticket


def update_ticket_priority(
    database: Session,
    ticket: Ticket,
    new_priority: TicketPriority,
    actor: User,
) -> Ticket:
    previous_priority = ticket.priority

    if previous_priority == new_priority:
        return ticket

    ticket.priority = new_priority

    add_ticket_history(
        database=database,
        ticket_id=ticket.id,
        actor_id=actor.id,
        action=TicketHistoryAction.PRIORITY_CHANGED,
        old_value=previous_priority.value,
        new_value=new_priority.value,
    )

    database.commit()

    updated_ticket = get_ticket_by_id(
        database=database,
        ticket_id=ticket.id,
    )

    if updated_ticket is None:
        raise RuntimeError("Ticket could not be retrieved after priority update")

    return updated_ticket

def create_ticket_message(
    database: Session,
    ticket: Ticket,
    author: User,
    content: str,
    is_internal: bool,
) -> TicketMessage:
    message = TicketMessage(
        ticket_id=ticket.id,
        author_id=author.id,
        content=content,
        is_internal=is_internal,
    )

    database.add(message)
    database.commit()

    created_message = get_ticket_message_by_id(
        database=database,
        message_id=message.id,
    )

    if created_message is None:
        raise RuntimeError("Message could not be retrieved after creation")

    return created_message


def get_ticket_message_by_id(
    database: Session,
    message_id: uuid.UUID,
) -> TicketMessage | None:
    statement = (
        select(TicketMessage)
        .options(
            joinedload(TicketMessage.author),
        )
        .where(TicketMessage.id == message_id)
    )

    return database.scalar(statement)


def get_ticket_messages(
    database: Session,
    ticket_id: uuid.UUID,
    current_user: User,
) -> list[TicketMessage]:
    statement = (
        select(TicketMessage)
        .options(
            joinedload(TicketMessage.author),
        )
        .where(TicketMessage.ticket_id == ticket_id)
        .order_by(TicketMessage.created_at.asc())
    )

    if current_user.role == UserRole.REQUESTER:
        statement = statement.where(
            TicketMessage.is_internal.is_(False),
        )

    return list(database.scalars(statement).all())


def user_can_write_ticket_message(
    current_user: User,
    ticket: Ticket,
) -> bool:
    if current_user.role == UserRole.ADMINISTRATOR:
        return True

    if current_user.role == UserRole.TECHNICIAN:
        return ticket.assigned_to_id == current_user.id

    return ticket.requester_id == current_user.id
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_TRIAGE = "in_triage"
    IN_PROGRESS = "in_progress"
    WAITING_REQUESTER = "waiting_requester"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    title: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[TicketStatus] = mapped_column(
        Enum(
            TicketStatus,
            name="ticket_status",
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ],
        ),
        default=TicketStatus.OPEN,
        nullable=False,
        index=True,
    )

    priority: Mapped[TicketPriority] = mapped_column(
        Enum(
            TicketPriority,
            name="ticket_priority",
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ],
        ),
        default=TicketPriority.MEDIUM,
        nullable=False,
        index=True,
    )

    requester_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    assigned_to_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    requester = relationship(
        "User",
        foreign_keys=[requester_id],
        back_populates="requested_tickets",
    )

    assigned_to = relationship(
        "User",
        foreign_keys=[assigned_to_id],
        back_populates="assigned_tickets",
    )
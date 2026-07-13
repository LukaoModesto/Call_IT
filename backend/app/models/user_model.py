import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


if TYPE_CHECKING:
    from app.models.ticket_model import Ticket


class UserRole(str, enum.Enum):
    REQUESTER = "requester"
    TECHNICIAN = "technician"
    ADMINISTRATOR = "administrator"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    full_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="user_role",
            values_callable=lambda enum_class: [
                role.value for role in enum_class
            ],
        ),
        default=UserRole.REQUESTER,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
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

    requested_tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket",
        foreign_keys="Ticket.requester_id",
        back_populates="requester",
        cascade="all, delete-orphan",
    )

    assigned_tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket",
        foreign_keys="Ticket.assigned_to_id",
        back_populates="assigned_to",
    )
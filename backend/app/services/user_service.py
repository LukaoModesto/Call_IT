import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user_model import User, UserRole
from app.schemas.user_schema import UserCreate


def get_user_by_id(
    database: Session,
    user_id: uuid.UUID,
) -> User | None:
    statement = select(User).where(User.id == user_id)

    return database.scalar(statement)


def get_user_by_email(
    database: Session,
    email: str,
) -> User | None:
    normalized_email = email.strip().lower()

    statement = select(User).where(
        User.email == normalized_email,
    )

    return database.scalar(statement)


def get_support_user_by_id(
    database: Session,
    user_id: uuid.UUID,
) -> User | None:
    statement = select(User).where(
        User.id == user_id,
        User.role.in_(
            [
                UserRole.TECHNICIAN,
                UserRole.ADMINISTRATOR,
            ]
        ),
        User.is_active.is_(True),
    )

    return database.scalar(statement)


def create_user(
    database: Session,
    user_data: UserCreate,
) -> User:
    user = User(
        full_name=user_data.full_name,
        email=str(user_data.email).strip().lower(),
        password_hash=hash_password(user_data.password),
        role=UserRole.REQUESTER,
    )

    database.add(user)
    database.commit()
    database.refresh(user)

    return user


def authenticate_user(
    database: Session,
    email: str,
    password: str,
) -> User | None:
    user = get_user_by_email(
        database=database,
        email=email,
    )

    if user is None:
        return None

    if not verify_password(
        plain_password=password,
        hashed_password=user.password_hash,
    ):
        return None

    return user
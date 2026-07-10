from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user_model import User, UserRole
from app.schemas.user_schema import UserCreate


def get_user_by_email(
    database: Session,
    email: str,
) -> User | None:
    statement = select(User).where(User.email == email.lower())

    return database.scalar(statement)


def create_user(
    database: Session,
    user_data: UserCreate,
) -> User:
    user = User(
        full_name=user_data.full_name,
        email=str(user_data.email).lower(),
        password_hash=hash_password(user_data.password),
        role=UserRole.REQUESTER,
    )

    database.add(user)
    database.commit()
    database.refresh(user)

    return user
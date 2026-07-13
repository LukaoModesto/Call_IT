from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserResponse
from app.services.user_service import create_user, get_user_by_email


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: UserCreate,
    database: Session = Depends(get_db),
) -> User:
    existing_user = get_user_by_email(
        database=database,
        email=str(user_data.email),
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    try:
        return create_user(
            database=database,
            user_data=user_data,
        )

    except IntegrityError as error:
        database.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        ) from error


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_authenticated_user(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user
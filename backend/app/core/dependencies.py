import uuid
from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.models.user_model import User, UserRole
from app.services.user_service import get_user_by_id


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    database: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        subject = payload.get("sub")
        token_type = payload.get("type")

        if subject is None or token_type != "access":
            raise credentials_exception

        user_id = uuid.UUID(subject)

    except (JWTError, ValueError) as error:
        raise credentials_exception from error

    user = get_user_by_id(
        database=database,
        user_id=user_id,
    )

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    return user


def require_roles(
    *allowed_roles: UserRole,
) -> Callable[..., User]:
    def role_dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )

        return current_user

    return role_dependency


get_current_requester = require_roles(
    UserRole.REQUESTER,
)

get_current_technician = require_roles(
    UserRole.TECHNICIAN,
)

get_current_administrator = require_roles(
    UserRole.ADMINISTRATOR,
)

get_current_support_member = require_roles(
    UserRole.TECHNICIAN,
    UserRole.ADMINISTRATOR,
)

get_current_any_user = require_roles(
    UserRole.REQUESTER,
    UserRole.TECHNICIAN,
    UserRole.ADMINISTRATOR,
)
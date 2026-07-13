from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from pwdlib import PasswordHash

from app.core.config import settings


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    expiration = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta is not None
        else timedelta(
            minutes=settings.access_token_expire_minutes,
        )
    )

    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expiration,
        "type": "access",
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )
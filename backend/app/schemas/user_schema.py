import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user_model import UserRole


class UserCreate(BaseModel):
    full_name: str = Field(
        min_length=3,
        max_length=120,
        examples=["Lucas Andrade"],
    )

    email: EmailStr = Field(
        examples=["lucas@example.com"],
    )

    password: str = Field(
        min_length=8,
        max_length=128,
        examples=["CallIT@123"],
    )

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, value: str) -> str:
        normalized_name = " ".join(value.split())

        if len(normalized_name) < 3:
            raise ValueError("Full name must contain at least 3 characters")

        return normalized_name

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class UserResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
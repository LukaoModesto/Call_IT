import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CategoryCreate(BaseModel):
    department_id: uuid.UUID

    name: str = Field(
        min_length=2,
        max_length=100,
        examples=["Hardware"],
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized_name = " ".join(value.split())

        if len(normalized_name) < 2:
            raise ValueError("Category name must contain at least 2 characters")

        return normalized_name


class CategoryResponse(BaseModel):
    id: uuid.UUID
    department_id: uuid.UUID
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
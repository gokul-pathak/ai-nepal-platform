import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SponsorPackageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    monthly_request_limit: int
    price_label: str | None
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SponsorLeadCreateRequest(BaseModel):
    organization_name: str = Field(min_length=2, max_length=255)
    contact_name: str = Field(min_length=2, max_length=255)
    email: str = Field(min_length=5, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    sponsor_type: str | None = Field(default=None, max_length=120)
    budget_range: str | None = Field(default=None, max_length=120)
    target_group: str | None = Field(default=None, max_length=255)
    message: str | None = Field(default=None, max_length=3000)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip()
        if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
            raise ValueError("Invalid email address")
        return normalized


class SponsorLeadCreateResponse(BaseModel):
    id: uuid.UUID
    message: str

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

        # Reject any input with whitespace
        if " " in normalized or "\t" in normalized or "\n" in normalized:
            raise ValueError("Invalid email address")

        # Ensure exactly one "@" character
        if normalized.count("@") != 1:
            raise ValueError("Invalid email address")

        # Split and ensure local and domain parts are non-empty
        local, domain = normalized.split("@")
        if not local or not domain:
            raise ValueError("Invalid email address")

        # Ensure domain contains at least one "." not at start or end
        if "." not in domain or domain.startswith(".") or domain.endswith("."):
            raise ValueError("Invalid email address")

        return normalized


class SponsorLeadCreateResponse(BaseModel):
    id: uuid.UUID
    message: str

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Integer, String, Text, Uuid, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class SponsorPackage(Base, TimestampMixin):
    """
    Represents sponsorship package tiers for supporting the platform.
    
    Each package defines a monthly request limit and pricing information
    for sponsor lead capture and reporting.
    """
    __tablename__ = "sponsor_packages"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(
        String(255), nullable=False,
        doc="Display name of package tier (Bronze, Silver, Gold, etc.)"
    )
    slug: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False, index=True,
        doc="URL-friendly identifier for the package"
    )
    monthly_request_limit: Mapped[int] = mapped_column(
        Integer, nullable=False,
        doc="Maximum API requests allowed per month under this package"
    )
    price_label: Mapped[str | None] = mapped_column(
        String(120), nullable=True,
        doc="Pricing tier display (e.g., '$100/month')"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        doc="Detailed package description and benefits"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true",
        doc="Whether package is available for new sponsors"
    )

    __table_args__ = (
        CheckConstraint("length(slug) > 0", name="ck_sponsor_package_slug_not_empty"),
        CheckConstraint("length(name) > 0", name="ck_sponsor_package_name_not_empty"),
        CheckConstraint("monthly_request_limit > 0", name="ck_sponsor_package_limit_positive"),
    )

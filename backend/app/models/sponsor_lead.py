import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, Uuid, func, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class SponsorLead(Base, TimestampMixin):
    """
    Represents a sponsorship inquiry or lead from an organization.
    
    Captures contact information and sponsorship details for follow-up
    and reporting. Status tracking enables lead management workflows.
    """
    __tablename__ = "sponsor_leads"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    organization_name: Mapped[str] = mapped_column(
        String(255), nullable=False,
        doc="Name of the sponsoring organization"
    )
    contact_name: Mapped[str] = mapped_column(
        String(255), nullable=False,
        doc="Primary contact person's name"
    )
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True,
        doc="Contact email address for follow-up"
    )
    phone: Mapped[str | None] = mapped_column(
        String(50), nullable=True,
        doc="Contact phone number"
    )
    sponsor_type: Mapped[str | None] = mapped_column(
        String(120), nullable=True,
        doc="Type of sponsorship (corporate, nonprofit, government, etc.)"
    )
    budget_range: Mapped[str | None] = mapped_column(
        String(120), nullable=True,
        doc="Sponsor's budget range (e.g., '10k-50k USD')"
    )
    target_group: Mapped[str | None] = mapped_column(
        String(255), nullable=True,
        doc="Target demographic for sponsorship impact"
    )
    message: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        doc="Additional details about sponsorship interest"
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="new", server_default="new",
        doc="Lead status (new, contacted, qualified, won, lost)"
    )

    __table_args__ = (
        # Index for list queries filtered by status (descending by created_at)
        Index("ix_sponsor_lead_status_created", "status", "created_at"),
        # Index for checking duplicate emails  
        Index("ix_sponsor_lead_email_created", "email", "created_at"),
        # String length validation (database-agnostic)
        CheckConstraint("length(organization_name) > 0", name="ck_sponsor_lead_org_not_empty"),
        CheckConstraint("length(contact_name) > 0", name="ck_sponsor_lead_contact_not_empty"),
        CheckConstraint("length(status) > 0", name="ck_sponsor_lead_status_not_empty"),
        # Note: Email format validation is done at application level via Pydantic schemas
    )

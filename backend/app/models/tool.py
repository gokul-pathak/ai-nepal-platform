import uuid
from datetime import datetime

from sqlalchemy import Boolean, String, Text, Uuid, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class Tool(Base, TimestampMixin):
    """
    Represents an AI tool available on the platform.
    
    Each tool has a unique slug for URL routing and can be activated/deactivated
    for feature rollouts and maintenance.
    """
    __tablename__ = "tools"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False, index=True,
        doc="URL-friendly identifier for the tool"
    )
    name: Mapped[str] = mapped_column(
        String(200), nullable=False,
        doc="Display name of the tool"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        doc="Detailed description of tool functionality"
    )
    category: Mapped[str | None] = mapped_column(
        String(120), nullable=True,
        doc="Category for tool organization (e.g., language, form, legal)"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true",
        doc="Whether tool is available for public use"
    )

    __table_args__ = (
        CheckConstraint("length(slug) > 0", name="ck_tool_slug_not_empty"),
        CheckConstraint("length(name) > 0", name="ck_tool_name_not_empty"),
    )

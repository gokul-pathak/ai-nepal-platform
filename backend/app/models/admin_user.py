import uuid
from datetime import datetime

from sqlalchemy import Boolean, String, Uuid, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class AdminUser(Base, TimestampMixin):
    """
    Represents an administrator user with access to admin endpoints and dashboards.
    
    Admin users are authenticated via email and password hash. The is_active flag
    allows disabling accounts without deletion.
    """
    __tablename__ = "admin_users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True,
        doc="Unique email address used for authentication"
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False,
        doc="Bcrypt password hash for secure authentication"
    )
    full_name: Mapped[str | None] = mapped_column(
        String(255), nullable=True,
        doc="Full name of the admin user"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true",
        doc="Whether account is active and can authenticate"
    )

    __table_args__ = (
        # String length validation (database-agnostic)
        CheckConstraint("length(password_hash) > 0", name="ck_admin_user_password_not_empty"),
        # Note: Email format validation is done at application level via Pydantic schemas
    )

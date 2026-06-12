"""production hardening: add indexes, constraints, and audit trails

Revision ID: 20260612_0002
Revises: 20260508_0001
Create Date: 2026-06-12

This migration adds production-grade improvements:
- Missing indexes for query performance (session_id, created_at, status)
- Composite indexes for common query patterns
- Foreign key cascade behavior for data integrity
- Check constraints for data validation
- Updated_at column for tool_usage table for audit trails
- Improved documentation and constraint naming
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260612_0002"
down_revision: str | None = "20260508_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply production hardening changes."""
    
    # 1. Add updated_at column to tool_usage (for audit trail consistency)
    op.add_column(
        "tool_usage",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    
    # 2. Update foreign key constraint on tool_usage.tool_id to use RESTRICT
    # This prevents orphaning usage records if a tool is deleted
    with op.batch_alter_table("tool_usage", schema=None) as batch_op:
        batch_op.drop_constraint("tool_usage_tool_id_fkey", type_="foreignkey")
        batch_op.create_foreign_key(
            "tool_usage_tool_id_fkey",
            "tools",
            ["tool_id"],
            ["id"],
            ondelete="RESTRICT",
        )
    
    # 3. Add performance indexes on tool_usage for common query patterns
    op.create_index(
        "ix_tool_usage_session_id",
        "tool_usage",
        ["session_id"],
        unique=False,
    )
    op.create_index(
        "ix_tool_usage_session_created",
        "tool_usage",
        ["session_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_tool_usage_tool_created",
        "tool_usage",
        ["tool_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_tool_usage_session_status",
        "tool_usage",
        ["session_id", "status"],
        unique=False,
    )
    
    # 4. Add indexes on sponsor_leads for filtering and aggregation
    op.create_index(
        "ix_sponsor_lead_email",
        "sponsor_leads",
        ["email"],
        unique=False,
    )
    op.create_index(
        "ix_sponsor_lead_status_created",
        "sponsor_leads",
        ["status", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_sponsor_lead_email_created",
        "sponsor_leads",
        ["email", "created_at"],
        unique=False,
    )
    
    # 5. Add check constraints to tool_usage for data integrity
    op.create_check_constraint(
        "ck_tool_usage_input_tokens_non_negative",
        "tool_usage",
        "input_tokens >= 0",
    )
    op.create_check_constraint(
        "ck_tool_usage_output_tokens_non_negative",
        "tool_usage",
        "output_tokens >= 0",
    )
    op.create_check_constraint(
        "ck_tool_usage_status_not_empty",
        "tool_usage",
        "length(status) > 0",
    )
    
    # 6. Add check constraints to tools for data integrity
    op.create_check_constraint(
        "ck_tool_slug_not_empty",
        "tools",
        "length(slug) > 0",
    )
    op.create_check_constraint(
        "ck_tool_name_not_empty",
        "tools",
        "length(name) > 0",
    )
    
    # 7. Add check constraints to sponsor_packages for data integrity
    op.create_check_constraint(
        "ck_sponsor_package_slug_not_empty",
        "sponsor_packages",
        "length(slug) > 0",
    )
    op.create_check_constraint(
        "ck_sponsor_package_name_not_empty",
        "sponsor_packages",
        "length(name) > 0",
    )
    op.create_check_constraint(
        "ck_sponsor_package_limit_positive",
        "sponsor_packages",
        "monthly_request_limit > 0",
    )
    
    # 8. Add check constraints to sponsor_leads for data integrity validation
    op.create_check_constraint(
        "ck_sponsor_lead_org_not_empty",
        "sponsor_leads",
        "length(organization_name) > 0",
    )
    op.create_check_constraint(
        "ck_sponsor_lead_contact_not_empty",
        "sponsor_leads",
        "length(contact_name) > 0",
    )
    op.create_check_constraint(
        "ck_sponsor_lead_status_not_empty",
        "sponsor_leads",
        "length(status) > 0",
    )
    # Note: Email format validation is done at application level via Pydantic schemas
    
    # 9. Add check constraints to admin_users for validation
    op.create_check_constraint(
        "ck_admin_user_password_not_empty",
        "admin_users",
        "length(password_hash) > 0",
    )
    # Note: Email format validation is done at application level via Pydantic schemas


def downgrade() -> None:
    """Revert production hardening changes."""
    
    # Drop all check constraints in reverse order
    op.drop_constraint("ck_admin_user_password_not_empty", "admin_users", type_="check")
    
    op.drop_constraint("ck_sponsor_lead_status_not_empty", "sponsor_leads", type_="check")
    op.drop_constraint("ck_sponsor_lead_contact_not_empty", "sponsor_leads", type_="check")
    op.drop_constraint("ck_sponsor_lead_org_not_empty", "sponsor_leads", type_="check")
    
    op.drop_constraint("ck_sponsor_package_limit_positive", "sponsor_packages", type_="check")
    op.drop_constraint("ck_sponsor_package_name_not_empty", "sponsor_packages", type_="check")
    op.drop_constraint("ck_sponsor_package_slug_not_empty", "sponsor_packages", type_="check")
    
    op.drop_constraint("ck_tool_name_not_empty", "tools", type_="check")
    op.drop_constraint("ck_tool_slug_not_empty", "tools", type_="check")
    
    op.drop_constraint("ck_tool_usage_status_not_empty", "tool_usage", type_="check")
    op.drop_constraint("ck_tool_usage_output_tokens_non_negative", "tool_usage", type_="check")
    op.drop_constraint("ck_tool_usage_input_tokens_non_negative", "tool_usage", type_="check")
    
    # Drop indexes on sponsor_leads
    op.drop_index("ix_sponsor_lead_email_created", table_name="sponsor_leads")
    op.drop_index("ix_sponsor_lead_status_created", table_name="sponsor_leads")
    op.drop_index("ix_sponsor_lead_email", table_name="sponsor_leads")
    
    # Drop indexes on tool_usage
    op.drop_index("ix_tool_usage_session_status", table_name="tool_usage")
    op.drop_index("ix_tool_usage_tool_created", table_name="tool_usage")
    op.drop_index("ix_tool_usage_session_created", table_name="tool_usage")
    op.drop_index("ix_tool_usage_session_id", table_name="tool_usage")
    
    # Restore original foreign key constraint on tool_usage
    with op.batch_alter_table("tool_usage", schema=None) as batch_op:
        batch_op.drop_constraint("tool_usage_tool_id_fkey", type_="foreignkey")
        batch_op.create_foreign_key(
            "tool_usage_tool_id_fkey",
            "tools",
            ["tool_id"],
            ["id"],
        )
    
    # Drop updated_at column from tool_usage
    op.drop_column("tool_usage", "updated_at")

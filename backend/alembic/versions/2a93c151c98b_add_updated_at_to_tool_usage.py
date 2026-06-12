"""add updated_at to tool_usage

Revision ID: 2a93c151c98b
Revises: 20260612_0002
Create Date: 2026-06-12 16:50:01.889114

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision: str = '2a93c151c98b'
down_revision: Union[str, None] = '20260612_0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

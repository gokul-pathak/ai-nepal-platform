"""add updated_at to tool_usage

Revision ID: 65920e0a9c71
Revises: 2a93c151c98b
Create Date: 2026-06-12 16:50:11.679500

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision: str = '65920e0a9c71'
down_revision: Union[str, None] = '2a93c151c98b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    pass


def downgrade():
    pass
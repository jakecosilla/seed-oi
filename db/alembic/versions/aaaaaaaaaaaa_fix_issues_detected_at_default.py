"""fix_issues_detected_at_default

Revision ID: aaaaaaaaaaaa
Revises: 999999999999
Create Date: 2026-04-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aaaaaaaaaaaa'
down_revision: Union[str, None] = '999999999999'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add server default for detected_at in issues table
    op.alter_column('issues', 'detected_at',
               existing_type=sa.DateTime(timezone=True),
               server_default=sa.text('now()'),
               existing_nullable=False)


def downgrade() -> None:
    # Remove server default for detected_at in issues table
    op.alter_column('issues', 'detected_at',
               existing_type=sa.DateTime(timezone=True),
               server_default=None,
               existing_nullable=False)

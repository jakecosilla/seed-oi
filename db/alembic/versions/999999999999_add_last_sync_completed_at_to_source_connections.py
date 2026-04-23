"""add_last_sync_completed_at_to_source_connections

Revision ID: 999999999999
Revises: 888888888888
Create Date: 2026-04-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '999999999999'
down_revision: Union[str, None] = '888888888888'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('source_connections', sa.Column('last_sync_completed_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('source_connections', 'last_sync_completed_at')

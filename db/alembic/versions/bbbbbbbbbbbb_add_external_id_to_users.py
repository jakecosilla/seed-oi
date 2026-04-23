"""add_external_id_to_users

Revision ID: bbbbbbbbbbbb
Revises: aaaaaaaaaaaa
Create Date: 2026-04-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bbbbbbbbbbbb'
down_revision: Union[str, None] = 'aaaaaaaaaaaa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add external_id column to users table
    op.add_column('users', sa.Column('external_id', sa.String(), nullable=True))
    # Create a unique index on external_id
    op.create_index(op.f('ix_users_external_id'), 'users', ['external_id'], unique=True)


def downgrade() -> None:
    # Remove index and column
    op.drop_index(op.f('ix_users_external_id'), table_name='users')
    op.drop_column('users', 'external_id')

"""add_entity_ref_to_issues

Revision ID: f23dc327704a
Revises: eacb8471e233
Create Date: 2026-04-23 14:11:33.081176

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f23dc327704a'
down_revision: Union[str, Sequence[str], None] = 'eacb8471e233'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('issues', sa.Column('primary_entity_type', sa.String(), nullable=True))
    op.add_column('issues', sa.Column('primary_entity_id', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('issues', 'primary_entity_id')
    op.drop_column('issues', 'primary_entity_type')

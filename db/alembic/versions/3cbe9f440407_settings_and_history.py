"""settings_and_history

Revision ID: 3cbe9f440407
Revises: 18a4480df57f
Create Date: 2026-04-23 13:05:57.163622

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3cbe9f440407'
down_revision: Union[str, Sequence[str], None] = '18a4480df57f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Settings table
    op.create_table(
        'settings',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('tenant_id', sa.UUID(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('plant_id', sa.UUID(), sa.ForeignKey('plants.id', ondelete='CASCADE'), nullable=True),
        sa.Column('category', sa.String(), nullable=False), # organization, plant, risk_rules, alert_rules, ai_assistant
        sa.Column('status', sa.String(), nullable=False, server_default='draft'), # draft, published
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('tenant_id', 'plant_id', 'category', 'status', name='uq_settings_scope_category_status')
    )

    # Settings history table for tracking changes
    op.create_table(
        'settings_history',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('setting_id', sa.UUID(), sa.ForeignKey('settings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('changed_by_user_id', sa.UUID(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )


def downgrade() -> None:
    op.drop_table('settings_history')
    op.drop_table('settings')

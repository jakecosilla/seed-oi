"""staging_and_mapping_layer

Revision ID: 18a4480df57f
Revises: ae95a90c444f
Create Date: 2026-04-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '18a4480df57f'
down_revision: Union[str, None] = 'ae95a90c444f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Raw Source Payloads
    op.create_table(
        'raw_source_payloads',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('tenant_id', sa.UUID(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_connection_id', sa.UUID(), sa.ForeignKey('source_connections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=False), # e.g., 'work_order', 'material'
        sa.Column('raw_payload', sa.JSON(), nullable=False), # JSON representing the external record
        sa.Column('status', sa.String(), nullable=False, server_default='pending'), # pending, validated, failed, mapped
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    # 2. Mapping Rules
    op.create_table(
        'mapping_rules',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('tenant_id', sa.UUID(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_connection_id', sa.UUID(), sa.ForeignKey('source_connections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=False),
        sa.Column('source_field', sa.String(), nullable=False),
        sa.Column('canonical_field', sa.String(), nullable=False),
        sa.Column('transformation_logic', sa.String(), nullable=True), # E.g., 'datetime_iso', 'uppercase'
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    # 3. Validation Logs
    op.create_table(
        'validation_logs',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('tenant_id', sa.UUID(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('raw_source_payload_id', sa.UUID(), sa.ForeignKey('raw_source_payloads.id', ondelete='CASCADE'), nullable=False),
        sa.Column('validation_type', sa.String(), nullable=False), # e.g., 'schema_error', 'mapping_error'
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False, server_default='error'), # warning, error
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )


def downgrade() -> None:
    op.drop_table('validation_logs')
    op.drop_table('mapping_rules')
    op.drop_table('raw_source_payloads')

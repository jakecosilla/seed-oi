"""add_bom_and_impact_fields

Revision ID: eacb8471e233
Revises: 3cbe9f440407
Create Date: 2026-04-23 14:10:48.176875

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eacb8471e233'
down_revision: Union[str, Sequence[str], None] = '3cbe9f440407'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Bill of Materials
    op.create_table(
        'bill_of_materials',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('product_id', sa.UUID(), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('material_id', sa.UUID(), sa.ForeignKey('materials.id', ondelete='CASCADE'), nullable=False),
        sa.Column('quantity_required', sa.Numeric(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    # 2. Sales Order Items
    op.create_table(
        'sales_order_items',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('sales_order_id', sa.UUID(), sa.ForeignKey('sales_orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_id', sa.UUID(), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('quantity', sa.Numeric(), nullable=False),
        sa.Column('unit_price', sa.Numeric(), nullable=True),
        sa.Column('tenant_id', sa.UUID(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    # 3. Add exposure fields to risks
    op.add_column('risks', sa.Column('revenue_exposure', sa.Numeric(), nullable=True))
    op.add_column('risks', sa.Column('cost_exposure', sa.Numeric(), nullable=True))


def downgrade() -> None:
    op.drop_column('risks', 'cost_exposure')
    op.drop_column('risks', 'revenue_exposure')
    op.drop_table('sales_order_items')
    op.drop_table('bill_of_materials')

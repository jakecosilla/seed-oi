"""canonical_operational_model

Revision ID: ae95a90c444f
Revises: 4e24283501fc
Create Date: 2026-04-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ae95a90c444f'
down_revision: Union[str, None] = '4e24283501fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# A helper to generate common traceability columns
def traceability_columns():
    return [
        sa.Column('tenant_id', sa.UUID(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('plant_id', sa.UUID(), sa.ForeignKey('plants.id', ondelete='SET NULL'), nullable=True),
        sa.Column('source_system', sa.String(), nullable=True),
        sa.Column('source_record_id', sa.String(), nullable=True),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    ]

def upgrade() -> None:
    # 1. Products
    op.create_table(
        'products',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('sku', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('unit_of_measure', sa.String(), nullable=False, server_default='EA'),
        *traceability_columns()
    )

    # 2. Materials (raw materials / components)
    op.create_table(
        'materials',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('unit_of_measure', sa.String(), nullable=False),
        sa.Column('lead_time_days', sa.Integer(), nullable=True),
        *traceability_columns()
    )

    # 3. Vendors
    op.create_table(
        'vendors',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('code', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('reliability_score', sa.Float(), nullable=True),
        *traceability_columns()
    )

    # 4. Customers
    op.create_table(
        'customers',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('code', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('priority_level', sa.String(), nullable=True),
        *traceability_columns()
    )

    # 5. Inventory Balances
    op.create_table(
        'inventory_balances',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('material_id', sa.UUID(), sa.ForeignKey('materials.id', ondelete='CASCADE'), nullable=True),
        sa.Column('product_id', sa.UUID(), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=True),
        sa.Column('location_code', sa.String(), nullable=True),
        sa.Column('quantity_on_hand', sa.Numeric(), nullable=False, server_default='0'),
        sa.Column('quantity_allocated', sa.Numeric(), nullable=False, server_default='0'),
        sa.Column('quantity_on_order', sa.Numeric(), nullable=False, server_default='0'),
        *traceability_columns()
    )

    # 6. Purchase Orders
    op.create_table(
        'purchase_orders',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('vendor_id', sa.UUID(), sa.ForeignKey('vendors.id', ondelete='SET NULL'), nullable=True),
        sa.Column('order_number', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('order_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expected_delivery_date', sa.DateTime(timezone=True), nullable=True),
        *traceability_columns()
    )

    # 7. Sales Orders
    op.create_table(
        'sales_orders',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('customer_id', sa.UUID(), sa.ForeignKey('customers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('order_number', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('order_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('requested_delivery_date', sa.DateTime(timezone=True), nullable=True),
        *traceability_columns()
    )

    # 8. Work Orders
    op.create_table(
        'work_orders',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('product_id', sa.UUID(), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('order_number', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('planned_start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('planned_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('target_quantity', sa.Numeric(), nullable=False),
        *traceability_columns()
    )

    # 9. Production Runs
    op.create_table(
        'production_runs',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('work_order_id', sa.UUID(), sa.ForeignKey('work_orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('actual_start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_quantity', sa.Numeric(), nullable=False, server_default='0'),
        *traceability_columns()
    )

    # 10. Shipments
    op.create_table(
        'shipments',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('sales_order_id', sa.UUID(), sa.ForeignKey('sales_orders.id', ondelete='CASCADE'), nullable=True),
        sa.Column('tracking_number', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('shipped_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('estimated_arrival_date', sa.DateTime(timezone=True), nullable=True),
        *traceability_columns()
    )

    # 11. Issues
    op.create_table(
        'issues',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('severity', sa.String(), nullable=False), # Critical, Warning, Monitor
        sa.Column('status', sa.String(), nullable=False), # Open, Resolved, Ignored
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False),
        *traceability_columns()
    )

    # 12. Risks
    op.create_table(
        'risks',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('issue_id', sa.UUID(), sa.ForeignKey('issues.id', ondelete='CASCADE'), nullable=False),
        sa.Column('risk_type', sa.String(), nullable=False), # Delay, Shortage, Bottleneck
        sa.Column('affected_entity_type', sa.String(), nullable=False), # e.g. WorkOrder, SalesOrder
        sa.Column('affected_entity_id', sa.String(), nullable=False), # Generic reference
        sa.Column('impact_score', sa.Float(), nullable=True),
        sa.Column('estimated_delay_days', sa.Integer(), nullable=True),
        *traceability_columns()
    )

    # 13. Scenarios
    op.create_table(
        'scenarios',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('issue_id', sa.UUID(), sa.ForeignKey('issues.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=False), # Proposed, Accepted, Rejected
        sa.Column('net_cost_impact', sa.Numeric(), nullable=True),
        sa.Column('delay_days_avoided', sa.Integer(), nullable=True),
        *traceability_columns()
    )

    # 14. Recommendations
    op.create_table(
        'recommendations',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('scenario_id', sa.UUID(), sa.ForeignKey('scenarios.id', ondelete='CASCADE'), nullable=False),
        sa.Column('action_type', sa.String(), nullable=False), # Expedite, Reallocate, Reschedule
        sa.Column('action_details', sa.JSON(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('rank', sa.Integer(), nullable=True),
        *traceability_columns()
    )


def downgrade() -> None:
    tables = [
        'recommendations', 'scenarios', 'risks', 'issues', 'shipments', 
        'production_runs', 'work_orders', 'sales_orders', 'purchase_orders', 
        'inventory_balances', 'customers', 'vendors', 'materials', 'products'
    ]
    for table in tables:
        op.drop_table(table)

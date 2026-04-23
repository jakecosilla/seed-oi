import uuid
from sqlalchemy import Column, String, DateTime, func, JSON, Numeric, Integer, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class TraceableMixin:
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    plant_id = Column(UUID(as_uuid=True), nullable=True)
    source_system = Column(String, nullable=True)
    source_record_id = Column(String, nullable=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class Setting(Base):
    __tablename__ = 'settings'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    plant_id = Column(UUID(as_uuid=True), nullable=True)
    category = Column(String, nullable=False)
    status = Column(String, nullable=False, default='draft')
    payload = Column(JSON, nullable=False)

class Material(Base, TraceableMixin):
    __tablename__ = 'materials'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    lead_time_days = Column(Integer, nullable=True)

class Product(Base, TraceableMixin):
    __tablename__ = 'products'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String, nullable=False)
    name = Column(String, nullable=False)

class BillOfMaterials(Base):
    __tablename__ = 'bill_of_materials'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False)
    material_id = Column(UUID(as_uuid=True), ForeignKey('materials.id'), nullable=False)
    quantity_required = Column(Numeric, nullable=False)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)

class InventoryBalance(Base, TraceableMixin):
    __tablename__ = 'inventory_balances'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    material_id = Column(UUID(as_uuid=True), ForeignKey('materials.id'), nullable=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=True)
    quantity_on_hand = Column(Numeric, nullable=False, default=0)
    quantity_allocated = Column(Numeric, nullable=False, default=0)
    quantity_on_order = Column(Numeric, nullable=False, default=0)

class PurchaseOrder(Base, TraceableMixin):
    __tablename__ = 'purchase_orders'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = Column(String, nullable=False)
    status = Column(String, nullable=False)
    expected_delivery_date = Column(DateTime(timezone=True), nullable=True)

class WorkOrder(Base, TraceableMixin):
    __tablename__ = 'work_orders'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False)
    order_number = Column(String, nullable=False)
    status = Column(String, nullable=False)
    planned_end_date = Column(DateTime(timezone=True), nullable=True)
    target_quantity = Column(Numeric, nullable=False)

class SalesOrder(Base, TraceableMixin):
    __tablename__ = 'sales_orders'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = Column(String, nullable=False)
    status = Column(String, nullable=False)
    requested_delivery_date = Column(DateTime(timezone=True), nullable=True)

class SalesOrderItem(Base):
    __tablename__ = 'sales_order_items'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sales_order_id = Column(UUID(as_uuid=True), ForeignKey('sales_orders.id'), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False)
    quantity = Column(Numeric, nullable=False)
    unit_price = Column(Numeric, nullable=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)

class Shipment(Base, TraceableMixin):
    __tablename__ = 'shipments'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sales_order_id = Column(UUID(as_uuid=True), ForeignKey('sales_orders.id'), nullable=True)
    status = Column(String, nullable=False)
    estimated_arrival_date = Column(DateTime(timezone=True), nullable=True)
    
class SourceConnection(Base):
    __tablename__ = 'source_connections'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    last_sync_completed_at = Column(DateTime(timezone=True), nullable=True)

class Issue(Base, TraceableMixin):
    __tablename__ = 'issues'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String, nullable=False) # Critical, Warning, Monitor
    status = Column(String, nullable=False) # Open, Resolved, Ignored
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    primary_entity_type = Column(String, nullable=True) # Material, PurchaseOrder, etc.
    primary_entity_id = Column(String, nullable=True)

class Risk(Base, TraceableMixin):
    __tablename__ = 'risks'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    issue_id = Column(UUID(as_uuid=True), ForeignKey('issues.id'), nullable=False)
    risk_type = Column(String, nullable=False) # Delay, Shortage, Bottleneck
    affected_entity_type = Column(String, nullable=False) # WorkOrder, SalesOrder, etc.
    affected_entity_id = Column(String, nullable=False)
    impact_score = Column(Float, nullable=True)
    estimated_delay_days = Column(Integer, nullable=True)
    revenue_exposure = Column(Numeric, nullable=True)
    cost_exposure = Column(Numeric, nullable=True)

class Scenario(Base, TraceableMixin):
    __tablename__ = 'scenarios'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    issue_id = Column(UUID(as_uuid=True), ForeignKey('issues.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=False, default='Proposed') # Proposed, Accepted, Rejected
    net_cost_impact = Column(Numeric, nullable=True)
    delay_days_avoided = Column(Integer, nullable=True)

class Recommendation(Base, TraceableMixin):
    __tablename__ = 'recommendations'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scenario_id = Column(UUID(as_uuid=True), ForeignKey('scenarios.id'), nullable=False)
    action_type = Column(String, nullable=False) # Expedite, Reallocate, Reschedule, Monitor
    action_details = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)
    rank = Column(Integer, nullable=True)

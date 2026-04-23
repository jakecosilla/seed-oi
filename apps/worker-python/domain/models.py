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

class InventoryBalance(Base, TraceableMixin):
    __tablename__ = 'inventory_balances'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    material_id = Column(UUID(as_uuid=True), nullable=True)
    quantity_on_hand = Column(Numeric, nullable=False, default=0)
    quantity_allocated = Column(Numeric, nullable=False, default=0)

class PurchaseOrder(Base, TraceableMixin):
    __tablename__ = 'purchase_orders'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = Column(String, nullable=False)
    status = Column(String, nullable=False)
    expected_delivery_date = Column(DateTime(timezone=True), nullable=True)
    
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

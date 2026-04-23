import uuid
from sqlalchemy import Column, String, DateTime, func, JSON, Float, Integer, Numeric, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class RawSourcePayload(Base):
    __tablename__ = 'raw_source_payloads'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    source_connection_id = Column(UUID(as_uuid=True), nullable=False)
    entity_type = Column(String, nullable=False)
    raw_payload = Column(JSON, nullable=False)
    status = Column(String, nullable=False, default='pending')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Setting(Base):
    __tablename__ = 'settings'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    plant_id = Column(UUID(as_uuid=True), nullable=True)
    category = Column(String, nullable=False)
    status = Column(String, nullable=False, default='draft') # draft, published
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class SettingHistory(Base):
    __tablename__ = 'settings_history'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    setting_id = Column(UUID(as_uuid=True), nullable=False)
    payload = Column(JSON, nullable=False)
    changed_by_user_id = Column(UUID(as_uuid=True), nullable=True)
class TraceableMixin:
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    plant_id = Column(UUID(as_uuid=True), nullable=True)
    source_system = Column(String, nullable=True)
    source_record_id = Column(String, nullable=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class Issue(Base, TraceableMixin):
    __tablename__ = 'issues'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    severity = Column(String, nullable=False) # Critical, Warning, Monitor
    status = Column(String, nullable=False) # Open, Resolved, Ignored
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    primary_entity_type = Column(String, nullable=True)
    primary_entity_id = Column(String, nullable=True)

class Risk(Base, TraceableMixin):
    __tablename__ = 'risks'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    issue_id = Column(UUID(as_uuid=True), nullable=False)
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
    issue_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False, default='Proposed') # Proposed, Accepted, Rejected
    net_cost_impact = Column(Numeric, nullable=True)
    delay_days_avoided = Column(Integer, nullable=True)

class Recommendation(Base, TraceableMixin):
    __tablename__ = 'recommendations'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scenario_id = Column(UUID(as_uuid=True), nullable=False)
    action_type = Column(String, nullable=False) # Expedite, Reallocate, Reschedule, Monitor
    action_details = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)
    rank = Column(Integer, nullable=True)

class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=True)
    entity_id = Column(String, nullable=True)
    actor_id = Column(String, nullable=True)
    actor_name = Column(String, nullable=True)
    payload = Column(JSON, nullable=True) # Before/After or details
    correlation_id = Column(String, nullable=True)

class SystemEvent(Base):
    __tablename__ = 'system_events'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    event_type = Column(String, nullable=False) # sync_failure, issue_gen_failure, assistant_request
    severity = Column(String, nullable=False, default='info') # info, warning, error, critical
    message = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    correlation_id = Column(String, nullable=True)

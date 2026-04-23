import uuid
from sqlalchemy import Column, String, DateTime, func, JSON
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
    changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

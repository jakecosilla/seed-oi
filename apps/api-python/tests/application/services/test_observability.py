import pytest
from unittest.mock import AsyncMock, MagicMock
from application.services.observability import ObservabilityService

@pytest.mark.asyncio
async def test_log_audit_success():
    # Arrange
    db_session = AsyncMock()
    service = ObservabilityService(db_session)
    
    # Act
    await service.log_audit(
        action="test_action",
        entity_type="test_entity",
        entity_id="123",
        payload={"key": "value"}
    )
    
    # Assert
    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()
    audit_obj = db_session.add.call_args[0][0]
    assert audit_obj.action == "test_action"
    assert audit_obj.entity_type == "test_entity"
    assert audit_obj.payload == {"key": "value"}

@pytest.mark.asyncio
async def test_emit_system_event_success():
    # Arrange
    db_session = AsyncMock()
    service = ObservabilityService(db_session)
    
    # Act
    await service.emit_system_event(
        event_type="test_event",
        message="test message",
        severity="warning",
        metadata={"meta": "data"}
    )
    
    # Assert
    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()
    event_obj = db_session.add.call_args[0][0]
    assert event_obj.event_type == "test_event"
    assert event_obj.severity == "warning"
    assert event_obj.message == "test message"
    assert event_obj.metadata_json == {"meta": "data"}

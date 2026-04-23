import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from domain.models import AuditLog, SystemEvent
from asgi_correlation_id import correlation_id
from infrastructure.logging import get_logger

logger = get_logger(__name__)

class ObservabilityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_audit(
        self, 
        action: str, 
        entity_type: str = None, 
        entity_id: str = None, 
        actor_id: str = None, 
        actor_name: str = None, 
        payload: dict = None
    ):
        """Track major system actions for compliance and debugging."""
        try:
            audit = AuditLog(
                id=uuid.uuid4(),
                timestamp=datetime.now(timezone.utc),
                action=action,
                entity_type=entity_type,
                entity_id=str(entity_id) if entity_id else None,
                actor_id=str(actor_id) if actor_id else None,
                actor_name=actor_name,
                payload=payload,
                correlation_id=correlation_id.get()
            )
            self.db.add(audit)
            await self.db.commit()
            logger.info("audit_log_created", action=action, entity_type=entity_type, entity_id=entity_id)
        except Exception as e:
            logger.error("failed_to_log_audit", error=str(e), action=action)
            # We don't want observability failures to break the main flow
            await self.db.rollback()

    async def emit_system_event(
        self, 
        event_type: str, 
        message: str, 
        severity: str = "info", 
        metadata: dict = None
    ):
        """Track system health events like sync failures or issue generation errors."""
        try:
            event = SystemEvent(
                id=uuid.uuid4(),
                timestamp=datetime.now(timezone.utc),
                event_type=event_type,
                severity=severity,
                message=message,
                metadata_json=metadata,
                correlation_id=correlation_id.get()
            )
            self.db.add(event)
            await self.db.commit()
            logger.info("system_event_emitted", event_type=event_type, severity=severity)
        except Exception as e:
            logger.error("failed_to_emit_system_event", error=str(e), event_type=event_type)
            await self.db.rollback()

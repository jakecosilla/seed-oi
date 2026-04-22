import asyncio
import json
from typing import Any, Dict, AsyncGenerator
import logging

logger = logging.getLogger(__name__)

# Basic in-memory pub-sub for demonstration/MVP.
# In a production distributed system, this would be backed by Redis Pub/Sub or Kafka.
class EventPublisher:
    def __init__(self):
        self._queues = []

    async def publish(self, event_type: str, payload: Dict[str, Any]):
        """
        Publish an event to all connected clients.
        Supported event_types:
          - source_sync_started
          - source_sync_completed
          - source_sync_failed
          - freshness_changed
          - issue_created
          - issue_updated
          - recommendation_updated
        """
        message = {
            "event": event_type,
            "data": payload
        }
        json_msg = json.dumps(message)
        logger.debug(f"Publishing event: {json_msg}")
        
        # Distribute to all connected client queues
        for q in self._queues:
            await q.put(json_msg)

    async def subscribe(self) -> AsyncGenerator[str, None]:
        """
        Subscribe to events. Yields JSON string messages.
        """
        q = asyncio.Queue()
        self._queues.append(q)
        try:
            while True:
                msg = await q.get()
                yield msg
        finally:
            self._queues.remove(q)

# Global instance for the FastAPI app
publisher = EventPublisher()

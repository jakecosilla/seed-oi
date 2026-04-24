import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, AsyncGenerator

try:
    import asyncpg
except ImportError:
    asyncpg = None

logger = logging.getLogger(__name__)

class EventBroker(ABC):
    @abstractmethod
    async def publish(self, event_type: str, payload: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def subscribe(self) -> AsyncGenerator[str, None]:
        pass


class InMemoryEventBroker(EventBroker):
    """
    Basic in-memory pub-sub for demonstration/MVP.
    Only works within a single process.
    """
    def __init__(self):
        self._queues = []

    async def publish(self, event_type: str, payload: Dict[str, Any]) -> None:
        message = {
            "event": event_type,
            "data": payload
        }
        json_msg = json.dumps(message)
        logger.debug(f"[InMemory] Publishing event: {json_msg}")
        
        for q in self._queues:
            await q.put(json_msg)

    async def subscribe(self) -> AsyncGenerator[str, None]:
        q = asyncio.Queue()
        self._queues.append(q)
        try:
            while True:
                msg = await q.get()
                yield msg
        finally:
            self._queues.remove(q)


class PostgresEventBroker(EventBroker):
    """
    Scalable pub-sub using PostgreSQL LISTEN/NOTIFY.
    Works across multiple processes and instances.
    """
    def __init__(self, database_url: str, channel: str = "seed_oi_events"):
        self.database_url = database_url
        self.channel = channel
        self._pool = None
        # Queues for distributing messages to local subscribers within this process
        self._local_queues = []
        self._listener_task = None

    async def _get_pool(self):
        if not self._pool:
            if not asyncpg:
                raise ImportError("asyncpg is required for PostgresEventBroker")
            self._pool = await asyncpg.create_pool(self.database_url)
        return self._pool

    async def publish(self, event_type: str, payload: Dict[str, Any]) -> None:
        message = {
            "event": event_type,
            "data": payload
        }
        json_msg = json.dumps(message)
        logger.debug(f"[Postgres] Publishing event to {self.channel}: {json_msg}")
        
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            # NOTIFY payload must be a string
            await conn.execute(f"SELECT pg_notify($1, $2)", self.channel, json_msg)

    def _on_notify(self, conn, pid, channel, payload):
        """Callback for asyncpg when a NOTIFY is received."""
        logger.debug(f"[Postgres] Received event on {channel}: {payload}")
        for q in self._local_queues:
            # q.put_nowait is safe here because we are in the event loop thread
            q.put_nowait(payload)

    async def _listen_loop(self):
        """Maintains the LISTEN connection and registers the callback."""
        pool = await self._get_pool()
        # We need a dedicated connection for LISTEN
        async with pool.acquire() as conn:
            await conn.add_listener(self.channel, self._on_notify)
            try:
                # Keep the connection alive forever
                while True:
                    await asyncio.sleep(3600)
            except asyncio.CancelledError:
                await conn.remove_listener(self.channel, self._on_notify)

    async def subscribe(self) -> AsyncGenerator[str, None]:
        q = asyncio.Queue()
        self._local_queues.append(q)
        
        # Start the listener task if it's the first subscriber
        if not self._listener_task:
            self._listener_task = asyncio.create_task(self._listen_loop())
            
        try:
            while True:
                msg = await q.get()
                yield msg
        finally:
            self._local_queues.remove(q)
            if not self._local_queues and self._listener_task:
                self._listener_task.cancel()
                self._listener_task = None


def get_event_broker(environment: str = "development", database_url: str = None) -> EventBroker:
    """
    Factory to get the appropriate event broker based on environment.
    Use PostgresEventBroker for production/scalable deployments,
    fallback to InMemoryEventBroker for basic local development if DB is not available.
    """
    if environment.lower() == "production" or database_url:
        logger.info("Initializing scalable PostgresEventBroker")
        return PostgresEventBroker(database_url)
    else:
        logger.info("Initializing single-process InMemoryEventBroker")
        return InMemoryEventBroker()

# Global instance initialization is deferred to application startup
publisher: EventBroker = InMemoryEventBroker()

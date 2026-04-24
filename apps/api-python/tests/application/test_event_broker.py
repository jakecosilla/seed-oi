import pytest
import asyncio
import json
from application.services.event_publisher import InMemoryEventBroker, PostgresEventBroker

@pytest.mark.asyncio
async def test_in_memory_event_broker():
    broker = InMemoryEventBroker()
    
    # Start subscription in a task
    subscription = broker.subscribe()
    
    # The subscription iterator doesn't yield immediately, we need to iterate it
    async def consume():
        async for msg in subscription:
            return msg

    consumer_task = asyncio.create_task(consume())
    
    # Yield control to allow the consumer to start waiting on the queue
    await asyncio.sleep(0.01)
    
    # Publish an event
    await broker.publish("test_event", {"key": "value"})
    
    # Wait for the consumer to receive it
    received_msg = await asyncio.wait_for(consumer_task, timeout=1.0)
    
    assert received_msg is not None
    data = json.loads(received_msg)
    assert data["event"] == "test_event"
    assert data["data"]["key"] == "value"


@pytest.mark.asyncio
async def test_postgres_event_broker_integration():
    """
    This test requires a local postgres instance running at the default URL.
    """
    database_url = "postgresql://postgres:postgres@localhost:5432/seed_oi"
    
    # We use two different broker instances to simulate two different processes
    publisher = PostgresEventBroker(database_url=database_url, channel="test_channel")
    subscriber = PostgresEventBroker(database_url=database_url, channel="test_channel")
    
    try:
        # We need to test the DB connection first to ensure we can run the test
        pool = await subscriber._get_pool()
        async with pool.acquire() as conn:
            await conn.execute("SELECT 1")
    except Exception:
        pytest.skip("PostgreSQL not available or connection failed.")

    # Start subscription
    sub_generator = subscriber.subscribe()
    
    async def consume():
        async for msg in sub_generator:
            return msg
            
    consumer_task = asyncio.create_task(consume())
    
    # Wait for listener task to start and establish LISTEN connection
    await asyncio.sleep(0.5)
    
    # Publish an event
    await publisher.publish("test_pg_event", {"hello": "world"})
    
    try:
        received_msg = await asyncio.wait_for(consumer_task, timeout=2.0)
        assert received_msg is not None
        data = json.loads(received_msg)
        assert data["event"] == "test_pg_event"
        assert data["data"]["hello"] == "world"
    finally:
        # Cleanup tasks
        if subscriber._listener_task:
            subscriber._listener_task.cancel()
        if publisher._pool:
            await publisher._pool.close()
        if subscriber._pool:
            await subscriber._pool.close()

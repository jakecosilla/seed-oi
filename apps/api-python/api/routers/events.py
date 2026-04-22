from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import asyncio

from application.services.event_publisher import publisher

router = APIRouter(prefix="/events", tags=["realtime"])

@router.get("/stream")
async def event_stream(request: Request):
    """
    Server-Sent Events (SSE) endpoint for real-time frontend updates.
    """
    async def event_generator():
        try:
            async for message in publisher.subscribe():
                if await request.is_disconnected():
                    break
                # SSE format requires "data: <payload>\n\n"
                yield f"data: {message}\n\n"
        except asyncio.CancelledError:
            pass
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Helper endpoint to test publishing an event locally
@router.post("/test-publish")
async def test_publish(event_type: str, entity_id: str):
    await publisher.publish(event_type, {"id": entity_id, "timestamp": "now"})
    return {"status": "event published"}

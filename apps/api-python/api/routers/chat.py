import uuid
import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional

from infrastructure.database import get_db
from infrastructure.security import get_current_user
from domain.models import User

from application.services.observability import ObservabilityService
from infrastructure.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None

class ChatResponse(BaseModel):
    response: str
    suggested_actions: List[str] = []
    sources: List[str] = []
    last_updated: str = ""

@router.post("/query", response_model=ChatResponse)
async def chat_query(
    request: ChatRequest,
    tenant_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from fastapi import HTTPException
    if tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized for this tenant")
    
    # Plant-level restriction check (if plant_id provided in context)
    if request.context and "plant_id" in request.context:
        from infrastructure.security import get_user_plant_ids
        allowed_plants = await get_user_plant_ids(current_user, db)
        req_plant = uuid.UUID(request.context["plant_id"])
        if req_plant not in allowed_plants:
             raise HTTPException(status_code=403, detail="Not authorized for this plant")

    obs = ObservabilityService(db)
    await obs.emit_system_event(
        event_type="assistant_request",
        message=f"Chat query: {request.message[:50]}...",
        severity="info",
        metadata={"query": request.message, "context": request.context}
    )
    now = datetime.datetime.now().strftime("%H:%M:%S")
    
    from application.services.chat_orchestrator import ChatOrchestrator
    from application.services.agent import SeedOIAgent
    from application.services.llm import get_chat_model
    
    orchestrator = ChatOrchestrator(db, tenant_id)
    chat_model = get_chat_model()
    agent = SeedOIAgent(db, chat_model, orchestrator)
    
    result = await agent.run(request.message, request.context, tenant_id)

    return ChatResponse(
        response=result.get("response", "I could not process your request."),
        suggested_actions=result.get("suggested_actions", []),
        sources=result.get("sources", []),
        last_updated=now
    )

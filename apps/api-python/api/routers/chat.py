import uuid
import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional

from infrastructure.database import get_db

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
    tenant_id: uuid.UUID = Query(uuid.UUID('00000000-0000-0000-0000-000000000000')),
    db: AsyncSession = Depends(get_db)
):
    msg = request.message.lower()
    now = datetime.datetime.now().strftime("%H:%M:%S")
    
    # Simple rule-based "AI" for the demo
    if "revenue" in msg or "risk" in msg:
        total_rev = 2450000 # Mocked
        response = f"Current operational analysis shows a total revenue exposure of ${total_rev:,.0f} across all active issues. The highest risk is currently linked to Material shortages in the Northern site."
        suggested = ["Show high-risk issues", "View impact map"]
        sources = ["Finance Ledger", "Salesforce Pipeline"]
    elif "delay" in msg:
        total_delay = 45 # Mocked
        response = f"There are approximately {total_delay} cumulative days of delay across your pending orders. I recommend reviewing the 'Expedite' scenarios to recover time."
        suggested = ["Open Scenarios", "View Timeline"]
        sources = ["Shipping Manifests", "Carrier APIs"]
    elif "scenario" in msg or "alternative" in msg:
        response = "I'm currently evaluating 3 alternative shipping routes to bypass the port congestion. Would you like to see the cost-benefit analysis for each?"
        suggested = ["Compare shipping routes", "See cost impact"]
        sources = ["Global Transit Map", "Pricing Engine"]
    else:
        response = "I'm monitoring your supply chain in real-time. You can ask about revenue exposure, pending delays, or bottleneck locations."
        suggested = ["What is the revenue at risk?", "Where are the bottlenecks?"]
        sources = ["ERP Systems", "IoT Sensor Data"]

    return ChatResponse(
        response=response,
        suggested_actions=suggested,
        sources=sources,
        last_updated=now
    )

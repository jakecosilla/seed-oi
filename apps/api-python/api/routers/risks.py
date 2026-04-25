from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
import uuid

from infrastructure.database import get_db
from api.dependencies.security import get_current_user
from domain.models import User

router = APIRouter(prefix="/risks", tags=["risks"])

class RiskSummaryResponse(BaseModel):
    total_active_risks: int
    critical_bottlenecks: int
    upcoming_delay_days: int
    total_exposure_usd: float
    on_track_percentage: float
    improved_capacity_count: int

class TimelineEvent(BaseModel):
    id: uuid.UUID
    date: str
    title: str
    severity: str
    delay_days: int
    revenue_exposure: float

class BottleneckItem(BaseModel):
    entity_id: str
    entity_type: str
    risk_count: int
    total_delay_days: int

@router.get("/summary", response_model=RiskSummaryResponse)
async def get_risk_summary(
    tenant_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized for this tenant")
    return RiskSummaryResponse(
        total_active_risks=24,
        critical_bottlenecks=5,
        upcoming_delay_days=128,
        total_exposure_usd=3450000.0,
        on_track_percentage=92.5,
        improved_capacity_count=3
    )

@router.get("/timeline", response_model=List[TimelineEvent])
async def get_risk_timeline(
    tenant_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized for this tenant")
    return [
        TimelineEvent(
            id=uuid.uuid4(),
            date="2026-04-25",
            title="Material Shortage: Northern Site",
            severity="Critical",
            delay_days=12,
            revenue_exposure=850000.0
        ),
        TimelineEvent(
            id=uuid.uuid4(),
            date="2026-04-28",
            title="Logistics Delay: Port Congestion",
            severity="High",
            delay_days=5,
            revenue_exposure=420000.0
        )
    ]

@router.get("/bottlenecks", response_model=List[BottleneckItem])
async def get_risk_bottlenecks(
    tenant_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized for this tenant")
    return [
        BottleneckItem(
            entity_type="WorkOrder",
            entity_id="WO-1002",
            risk_count=3,
            total_delay_days=15
        ),
        BottleneckItem(
            entity_type="Plant",
            entity_id="Northern Site",
            risk_count=8,
            total_delay_days=45
        )
    ]

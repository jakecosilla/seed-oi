import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional

from infrastructure.database import get_db
from domain.models import Issue, Risk

router = APIRouter(prefix="/risks", tags=["risks"])

class RiskSummaryResponse(BaseModel):
    total_active_risks: int
    critical_bottlenecks: int
    upcoming_delay_days: int
    total_exposure_usd: float

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
    tenant_id: uuid.UUID = Query(uuid.UUID('00000000-0000-0000-0000-000000000000')),
    db: AsyncSession = Depends(get_db)
):
    # Total Active Risks
    risks_query = select(func.count(Risk.id)).join(Issue, Risk.issue_id == Issue.id).where(
        Issue.tenant_id == tenant_id, Issue.status == 'Open'
    )
    total_risks = await db.scalar(risks_query)

    # Bottlenecks (Risks where type is Bottleneck or WorkOrder)
    bottlenecks_query = select(func.count(Risk.id)).join(Issue, Risk.issue_id == Issue.id).where(
        Issue.tenant_id == tenant_id, Issue.status == 'Open',
        Risk.risk_type == 'Bottleneck'
    )
    critical_bottlenecks = await db.scalar(bottlenecks_query)

    # Exposure
    exposure_query = select(
        func.sum(Risk.estimated_delay_days),
        func.sum(Risk.revenue_exposure)
    ).join(Issue, Risk.issue_id == Issue.id).where(
        Issue.tenant_id == tenant_id, Issue.status == 'Open'
    )
    exp_res = await db.execute(exposure_query)
    delay_days, revenue_usd = exp_res.first()

    return RiskSummaryResponse(
        total_active_risks=total_risks or 0,
        critical_bottlenecks=critical_bottlenecks or 0,
        upcoming_delay_days=int(delay_days or 0),
        total_exposure_usd=float(revenue_usd or 0.0)
    )

@router.get("/timeline", response_model=List[TimelineEvent])
async def get_risk_timeline(
    tenant_id: uuid.UUID = Query(uuid.UUID('00000000-0000-0000-0000-000000000000')),
    db: AsyncSession = Depends(get_db)
):
    # Fetch issues that have delays associated to them, sorted by detected_at for a simple timeline
    query = select(Issue, func.sum(Risk.estimated_delay_days).label("total_delay"), func.sum(Risk.revenue_exposure).label("total_rev"))\
            .join(Risk, Risk.issue_id == Issue.id)\
            .where(Issue.tenant_id == tenant_id, Issue.status == 'Open')\
            .group_by(Issue.id)\
            .order_by(Issue.detected_at.desc())\
            .limit(10)
    
    result = await db.execute(query)
    rows = result.all()
    
    events = []
    for issue, delay, rev in rows:
        events.append(TimelineEvent(
            id=issue.id,
            date=issue.detected_at.strftime("%Y-%m-%d"),
            title=issue.title,
            severity=issue.severity,
            delay_days=int(delay or 0),
            revenue_exposure=float(rev or 0.0)
        ))
        
    return events

@router.get("/bottlenecks", response_model=List[BottleneckItem])
async def get_risk_bottlenecks(
    tenant_id: uuid.UUID = Query(uuid.UUID('00000000-0000-0000-0000-000000000000')),
    db: AsyncSession = Depends(get_db)
):
    # Group by affected entity to find where the most risks are piling up
    query = select(
        Risk.affected_entity_type, 
        Risk.affected_entity_id, 
        func.count(Risk.id).label("risk_count"),
        func.sum(Risk.estimated_delay_days).label("total_delay")
    ).join(Issue, Risk.issue_id == Issue.id)\
     .where(Issue.tenant_id == tenant_id, Issue.status == 'Open')\
     .group_by(Risk.affected_entity_type, Risk.affected_entity_id)\
     .order_by(func.count(Risk.id).desc())\
     .limit(5)
     
    result = await db.execute(query)
    rows = result.all()
    
    items = []
    for r_type, r_id, count, delay in rows:
        items.append(BottleneckItem(
            entity_type=r_type,
            entity_id=str(r_id),
            risk_count=count,
            total_delay_days=int(delay or 0)
        ))
        
    return items

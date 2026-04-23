import uuid
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from infrastructure.database import get_db
from domain.models import Issue, Scenario, Recommendation, Risk

router = APIRouter(prefix="/scenarios", tags=["scenarios"])

class IssueSimpleDTO(BaseModel):
    id: uuid.UUID
    title: str
    severity: str
    detected_at: str

class RecommendationDTO(BaseModel):
    id: uuid.UUID
    action_type: str
    action_details: Optional[Dict[str, Any]]
    confidence_score: Optional[float]
    rank: Optional[int]

class ScenarioDTO(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    status: str
    net_cost_impact: float
    delay_days_avoided: int
    recommendations: List[RecommendationDTO] = []

class BaselineMetricsDTO(BaseModel):
    total_delay_days: int
    revenue_at_risk: float

class ScenarioComparisonDTO(BaseModel):
    issue_id: uuid.UUID
    issue_title: str
    issue_description: Optional[str]
    last_synced_at: Optional[str]
    baseline: BaselineMetricsDTO
    options: List[ScenarioDTO]

@router.get("/issues", response_model=List[IssueSimpleDTO])
async def get_evaluable_issues(
    tenant_id: uuid.UUID = Query(uuid.UUID('00000000-0000-0000-0000-000000000000')),
    db: AsyncSession = Depends(get_db)
):
    # Get issues that have scenarios generated
    query = select(Issue).join(Scenario, Scenario.issue_id == Issue.id)\
            .where(Issue.tenant_id == tenant_id, Issue.status == 'Open')\
            .group_by(Issue.id)\
            .order_by(Issue.detected_at.desc())
            
    result = await db.execute(query)
    issues = result.scalars().all()
    
    return [
        IssueSimpleDTO(
            id=i.id,
            title=i.title,
            severity=i.severity,
            detected_at=i.detected_at.isoformat()
        ) for i in issues
    ]

@router.get("/{issue_id}/comparison", response_model=ScenarioComparisonDTO)
async def get_scenario_comparison(
    issue_id: uuid.UUID,
    tenant_id: uuid.UUID = Query(uuid.UUID('00000000-0000-0000-0000-000000000000')),
    db: AsyncSession = Depends(get_db)
):
    # Fetch Issue
    issue_query = select(Issue).where(Issue.id == issue_id, Issue.tenant_id == tenant_id)
    issue_result = await db.execute(issue_query)
    issue = issue_result.scalars().first()
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
        
    # Calculate Baseline from Risks
    risk_query = select(
        func.sum(Risk.estimated_delay_days),
        func.sum(Risk.revenue_exposure)
    ).where(Risk.issue_id == issue_id)
    risk_res = await db.execute(risk_query)
    baseline_delay, baseline_revenue = risk_res.first()
    
    # Fetch Scenarios
    scen_query = select(Scenario).where(Scenario.issue_id == issue_id).order_by(Scenario.net_cost_impact.asc())
    scen_result = await db.execute(scen_query)
    scenarios = scen_result.scalars().all()
    
    options = []
    for s in scenarios:
        # Fetch Recommendations
        rec_query = select(Recommendation).where(Recommendation.scenario_id == s.id).order_by(Recommendation.rank)
        rec_result = await db.execute(rec_query)
        recs = rec_result.scalars().all()
        
        options.append(ScenarioDTO(
            id=s.id,
            name=s.name,
            description=s.description,
            status=s.status,
            net_cost_impact=float(s.net_cost_impact or 0),
            delay_days_avoided=int(s.delay_days_avoided or 0),
            recommendations=[
                RecommendationDTO(
                    id=r.id,
                    action_type=r.action_type,
                    action_details=r.action_details,
                    confidence_score=r.confidence_score,
                    rank=r.rank
                ) for r in recs
            ]
        ))
        
    return ScenarioComparisonDTO(
        issue_id=issue.id,
        issue_title=issue.title,
        issue_description=issue.description,
        last_synced_at=issue.detected_at.isoformat(), # Proxy for freshness
        baseline=BaselineMetricsDTO(
            total_delay_days=int(baseline_delay or 0),
            revenue_at_risk=float(baseline_revenue or 0)
        ),
        options=options
    )

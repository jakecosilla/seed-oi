import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from infrastructure.database import get_db
from domain.models import Issue, Risk, Scenario, Recommendation

router = APIRouter(prefix="/overview", tags=["overview"])

class SummaryResponse(BaseModel):
    total_open_issues: int
    critical_issues: int
    total_revenue_at_risk: float
    total_delay_days: int

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
    net_cost_impact: Optional[float]
    delay_days_avoided: Optional[int]
    recommendations: List[RecommendationDTO] = []

class RiskDTO(BaseModel):
    id: uuid.UUID
    risk_type: str
    affected_entity_type: str
    affected_entity_id: str
    revenue_exposure: Optional[float]
    estimated_delay_days: Optional[int]

class IssueResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str]
    severity: str
    status: str
    primary_entity_type: Optional[str]
    primary_entity_id: Optional[str]
    risks: List[RiskDTO] = []
    top_scenario: Optional[ScenarioDTO] = None

@router.get("/summary", response_model=SummaryResponse)
async def get_overview_summary(
    tenant_id: uuid.UUID = Query(uuid.UUID('00000000-0000-0000-0000-000000000000')),
    db: AsyncSession = Depends(get_db)
):
    # 1. Total Open Issues
    issues_query = select(func.count()).where(Issue.tenant_id == tenant_id, Issue.status == 'Open')
    total_issues = await db.scalar(issues_query)
    
    # 2. Critical Issues
    critical_query = select(func.count()).where(Issue.tenant_id == tenant_id, Issue.status == 'Open', Issue.severity == 'Critical')
    critical_issues = await db.scalar(critical_query)
    
    # 3. Revenue & Delay Exposure (from Risks tied to Open Issues)
    exposure_query = select(
        func.sum(Risk.revenue_exposure), 
        func.sum(Risk.estimated_delay_days)
    ).join(Issue, Risk.issue_id == Issue.id).where(
        Issue.tenant_id == tenant_id,
        Issue.status == 'Open'
    )
    exposure_result = await db.execute(exposure_query)
    total_revenue, total_delay = exposure_result.first()
    
    return SummaryResponse(
        total_open_issues=total_issues or 0,
        critical_issues=critical_issues or 0,
        total_revenue_at_risk=float(total_revenue or 0),
        total_delay_days=int(total_delay or 0)
    )

@router.get("/issues", response_model=List[IssueResponse])
async def get_overview_issues(
    tenant_id: uuid.UUID = Query(uuid.UUID('00000000-0000-0000-0000-000000000000')),
    db: AsyncSession = Depends(get_db)
):
    # Fetch open issues
    query = select(Issue).where(Issue.tenant_id == tenant_id, Issue.status == 'Open').order_by(Issue.detected_at.desc())
    result = await db.execute(query)
    issues = result.scalars().all()
    
    response_data = []
    
    for issue in issues:
        # Fetch Risks
        risk_query = select(Risk).where(Risk.issue_id == issue.id)
        risk_res = await db.execute(risk_query)
        risks = risk_res.scalars().all()
        
        # Fetch Top Scenario
        scenario_query = select(Scenario).where(Scenario.issue_id == issue.id).limit(1)
        scenario_res = await db.execute(scenario_query)
        scenario = scenario_res.scalars().first()
        
        scenario_dto = None
        if scenario:
            # Fetch Recommendations for Scenario
            rec_query = select(Recommendation).where(Recommendation.scenario_id == scenario.id).order_by(Recommendation.rank)
            rec_res = await db.execute(rec_query)
            recs = rec_res.scalars().all()
            
            scenario_dto = ScenarioDTO(
                id=scenario.id,
                name=scenario.name,
                description=scenario.description,
                net_cost_impact=float(scenario.net_cost_impact) if scenario.net_cost_impact else None,
                delay_days_avoided=scenario.delay_days_avoided,
                recommendations=[
                    RecommendationDTO(
                        id=r.id,
                        action_type=r.action_type,
                        action_details=r.action_details,
                        confidence_score=r.confidence_score,
                        rank=r.rank
                    ) for r in recs
                ]
            )
            
        response_data.append(
            IssueResponse(
                id=issue.id,
                title=issue.title,
                description=issue.description,
                severity=issue.severity,
                status=issue.status,
                primary_entity_type=issue.primary_entity_type,
                primary_entity_id=issue.primary_entity_id,
                risks=[
                    RiskDTO(
                        id=r.id,
                        risk_type=r.risk_type,
                        affected_entity_type=r.affected_entity_type,
                        affected_entity_id=r.affected_entity_id,
                        revenue_exposure=float(r.revenue_exposure) if r.revenue_exposure else None,
                        estimated_delay_days=r.estimated_delay_days
                    ) for r in risks
                ],
                top_scenario=scenario_dto
            )
        )
        
    return response_data

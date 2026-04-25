import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from infrastructure.database import get_db
from api.dependencies.security import get_current_user
from application.security.authorization import auth_service
from domain.models import User

router = APIRouter(prefix="/overview", tags=["overview"])

class SummaryResponse(BaseModel):
    total_open_issues: int
    critical_issues: int
    total_revenue_at_risk: float
    total_delay_days: int
    on_track_percentage: float
    improved_count: int
    available_capacity_pct: float
    active_opportunities: int

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

class HealthSignal(BaseModel):
    id: uuid.UUID
    category: str  # 'Healthy', 'Improved', 'Capacity', 'Opportunity'
    title: str
    description: str
    metric_value: Optional[str]
    metric_trend: Optional[str]  # 'up', 'down', 'stable'
    impact_area: str

@router.get("/summary", response_model=SummaryResponse)
async def get_overview_summary(
    tenant_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    auth_service.check_tenant_access(current_user, tenant_id)
    # Mock data for demo
    return SummaryResponse(
        total_open_issues=12,
        critical_issues=3,
        total_revenue_at_risk=2450000.0,
        total_delay_days=45,
        on_track_percentage=88.5,
        improved_count=5,
        available_capacity_pct=15.2,
        active_opportunities=4
    )

@router.get("/health", response_model=List[HealthSignal])
async def get_overview_health(
    tenant_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    auth_service.check_tenant_access(current_user, tenant_id)
    # Mock data for demo
    return [
        HealthSignal(
            id=uuid.uuid4(),
            category="Healthy",
            title="Material Inventory: Southern Site",
            description="Inventory levels for core components are stable with 14 days of safety stock.",
            metric_value="98%",
            metric_trend="stable",
            impact_area="Production"
        ),
        HealthSignal(
            id=uuid.uuid4(),
            category="Improved",
            title="Lead Time: Vendor Alpha",
            description="Average lead time has decreased by 2 days over the last 30 days.",
            metric_value="-15%",
            metric_trend="down",
            impact_area="Supply Chain"
        ),
        HealthSignal(
            id=uuid.uuid4(),
            category="Capacity",
            title="Line 4 Availability",
            description="Line 4 has 20% available capacity next week due to early maintenance completion.",
            metric_value="20%",
            metric_trend="up",
            impact_area="Manufacturing"
        ),
        HealthSignal(
            id=uuid.uuid4(),
            category="Opportunity",
            title="Consolidated Shipping",
            description="Opportunity to consolidate 5 pending shipments from Vendor Beta to save $12k.",
            metric_value="$12,000",
            metric_trend="up",
            impact_area="Logistics"
        )
    ]

@router.get("/issues", response_model=List[IssueResponse])
async def get_overview_issues(
    tenant_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    auth_service.check_tenant_access(current_user, tenant_id)
    # Mock data for demo
    issue_id = uuid.UUID('11111111-1111-1111-1111-111111111111')
    return [
        IssueResponse(
            id=issue_id,
            title="Material Shortage: Northern Site",
            description="Critical shortage of Material X affecting 3 work orders.",
            severity="Critical",
            status="Open",
            primary_entity_type="Material",
            primary_entity_id="MAT-X-001",
            risks=[
                RiskDTO(
                    id=uuid.uuid4(),
                    risk_type="Revenue Exposure",
                    affected_entity_type="SalesOrder",
                    affected_entity_id="SO-992",
                    revenue_exposure=850000.0,
                    estimated_delay_days=12
                )
            ],
            top_scenario=ScenarioDTO(
                id=uuid.uuid4(),
                name="Expedite Air Freight",
                description="Bypass sea port congestion by using air freight for critical materials.",
                net_cost_impact=15000.0,
                delay_days_avoided=10,
                recommendations=[
                    RecommendationDTO(
                        id=uuid.uuid4(),
                        action_type="Expedite",
                        action_details={"Carrier": "FedEx", "Route": "SFO-NYC"},
                        confidence_score=0.95,
                        rank=1
                    )
                ]
            )
        )
    ]

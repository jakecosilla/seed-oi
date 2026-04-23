import uuid
import datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from infrastructure.database import get_db
from api.dependencies.security import get_current_user, require_role
from domain.models import User

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
    tenant_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized for this tenant")
    return [
        IssueSimpleDTO(
            id=uuid.UUID('11111111-1111-1111-1111-111111111111'),
            title="Material Shortage: Northern Site",
            severity="Critical",
            detected_at=datetime.datetime.now().isoformat()
        )
    ]

@router.get("/{issue_id}/comparison", response_model=ScenarioComparisonDTO)
async def get_scenario_comparison(
    issue_id: uuid.UUID,
    tenant_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized for this tenant")
    return ScenarioComparisonDTO(
        issue_id=issue_id,
        issue_title="Material Shortage: Northern Site",
        issue_description="Critical shortage of Material X affecting 3 work orders.",
        last_synced_at=datetime.datetime.now().isoformat(),
        baseline=BaselineMetricsDTO(
            total_delay_days=15,
            revenue_at_risk=850000.0
        ),
        options=[
            ScenarioDTO(
                id=uuid.uuid4(),
                name="Expedite Air Freight",
                description="Bypass sea port congestion by using air freight for critical materials.",
                status="Recommended",
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
            ),
            ScenarioDTO(
                id=uuid.uuid4(),
                name="Reallocate from Southern Plant",
                description="Transfer 500 units of Material X from Southern Site inventory.",
                status="Alternative",
                net_cost_impact=2000.0,
                delay_days_avoided=4,
                recommendations=[
                    RecommendationDTO(
                        id=uuid.uuid4(),
                        action_type="Reallocate",
                        action_details={"Source": "Southern Site", "Qty": "500"},
                        confidence_score=0.85,
                        rank=2
                    )
                ]
            )
        ]
    )

@router.post("/{scenario_id}/execute")
async def execute_scenario(
    scenario_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "operator"]))
):
    """
    Execute a chosen scenario. This is a major system action that requires auditing.
    """
    # Logic to trigger actual execution would go here
    from application.services.observability import ObservabilityService
    obs = ObservabilityService(db)
    await obs.log_audit(
        action="execute_scenario",
        entity_type="scenario",
        entity_id=scenario_id,
        payload={"execution_status": "triggered"}
    )
    return {"status": "execution_triggered", "scenario_id": scenario_id}

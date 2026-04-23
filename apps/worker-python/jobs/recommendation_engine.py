import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from domain.models import Issue, Risk, Scenario, Recommendation

logger = logging.getLogger(__name__)

async def generate_recommendations_for_issue(db: AsyncSession, issue: Issue):
    """
    Generates and ranks recommendations for a specific issue.
    """
    logger.info(f"Generating recommendations for issue {issue.id}: {issue.title}")
    
    # 1. Fetch context (downstream risks) to understand the impact
    risks_query = select(Risk).where(Risk.issue_id == issue.id)
    risks_result = await db.execute(risks_query)
    risks = risks_result.scalars().all()
    
    # Clean up existing scenarios/recommendations for this issue to regenerate
    # In production, we might version these instead of deleting.
    old_scenarios_query = select(Scenario).where(Scenario.issue_id == issue.id)
    old_scenarios_result = await db.execute(old_scenarios_query)
    old_scenarios = old_scenarios_result.scalars().all()
    for os in old_scenarios:
        await db.execute(delete(Recommendation).where(Recommendation.scenario_id == os.id))
        await db.delete(os)
    
    # Calculate total exposure from risks to inform scoring
    total_delay_exposure = sum((r.estimated_delay_days or 0) for r in risks)
    total_revenue_exposure = sum((float(r.revenue_exposure or 0)) for r in risks)
    
    scenarios = []
    
    # 2. Strategy 1: Expedite
    # Action: Pay a premium to expedite shipping from supplier
    expedite_cost = 5000.0  # Simulated cost
    days_saved = min(total_delay_exposure, 5) # Assume we can save up to 5 days
    expedite_confidence = 0.85
    expedite_complexity = 2 # 1-10 scale
    
    expedite_score = calculate_score(
        severity=issue.severity,
        cost=expedite_cost,
        time_saved=days_saved,
        complexity=expedite_complexity,
        confidence=expedite_confidence,
        revenue_protected=total_revenue_exposure
    )
    
    scenarios.append({
        "name": "Expedite Delivery",
        "description": "Approve premium air freight to reduce delay.",
        "net_cost_impact": expedite_cost,
        "delay_days_avoided": days_saved,
        "score": expedite_score,
        "recommendations": [
            {
                "action_type": "Expedite",
                "action_details": {"method": "Air Freight", "estimated_cost": expedite_cost},
                "confidence_score": expedite_confidence
            }
        ]
    })
    
    # 3. Strategy 2: Reallocate
    # Action: Reallocate inventory from lower-priority orders
    reallocate_cost = 500.0 # Administrative/handling cost
    days_saved_realloc = min(total_delay_exposure, 10)
    reallocate_confidence = 0.60
    reallocate_complexity = 8 # High complexity
    
    realloc_score = calculate_score(
        severity=issue.severity,
        cost=reallocate_cost,
        time_saved=days_saved_realloc,
        complexity=reallocate_complexity,
        confidence=reallocate_confidence,
        revenue_protected=total_revenue_exposure
    )
    
    scenarios.append({
        "name": "Reallocate Inventory",
        "description": "Divert existing stock from standard orders to priority work orders.",
        "net_cost_impact": reallocate_cost,
        "delay_days_avoided": days_saved_realloc,
        "score": realloc_score,
        "recommendations": [
            {
                "action_type": "Reallocate",
                "action_details": {"source": "Standard Stock", "target": "Priority WO"},
                "confidence_score": reallocate_confidence
            },
            {
                "action_type": "Resequence",
                "action_details": {"target": "Production Schedule"},
                "confidence_score": 0.70
            }
        ]
    })
    
    # 4. Strategy 3: Monitor
    monitor_score = calculate_score(
        severity=issue.severity,
        cost=0.0,
        time_saved=0,
        complexity=1,
        confidence=0.95,
        revenue_protected=0.0
    )
    
    scenarios.append({
        "name": "Monitor Situation",
        "description": "No immediate action. Track supplier updates.",
        "net_cost_impact": 0.0,
        "delay_days_avoided": 0,
        "score": monitor_score,
        "recommendations": [
            {
                "action_type": "Monitor",
                "action_details": {"frequency": "Daily"},
                "confidence_score": 0.95
            }
        ]
    })
    
    # 5. Rank and Persist
    # Sort scenarios by score descending
    scenarios.sort(key=lambda x: x["score"], reverse=True)
    
    for rank_idx, s_data in enumerate(scenarios):
        # Create Scenario
        scenario = Scenario(
            issue_id=issue.id,
            tenant_id=issue.tenant_id,
            plant_id=issue.plant_id,
            name=s_data["name"],
            description=s_data["description"],
            status="Proposed",
            net_cost_impact=s_data["net_cost_impact"],
            delay_days_avoided=s_data["delay_days_avoided"]
        )
        db.add(scenario)
        await db.flush() # Get scenario ID
        
        # Create Recommendations for this Scenario
        for rec_data in s_data["recommendations"]:
            rec = Recommendation(
                scenario_id=scenario.id,
                tenant_id=issue.tenant_id,
                plant_id=issue.plant_id,
                action_type=rec_data["action_type"],
                action_details=rec_data["action_details"],
                confidence_score=rec_data["confidence_score"],
                rank=rank_idx + 1 # 1-based ranking
            )
            db.add(rec)

def calculate_score(severity: str, cost: float, time_saved: int, complexity: int, confidence: float, revenue_protected: float) -> float:
    """
    Deterministic scoring function for ranking scenarios.
    Higher score is better.
    """
    # Base value of saving time vs cost
    value_score = (time_saved * 1000) + (revenue_protected * 0.1) - cost
    
    # Penalize for complexity (1-10)
    complexity_penalty = (complexity / 10.0) * 0.5 # Up to 50% penalty
    
    # Adjust for confidence
    adjusted_score = value_score * confidence * (1.0 - complexity_penalty)
    
    # Bump scores if severity is critical and we are taking action
    if severity == "Critical" and time_saved > 0:
        adjusted_score *= 1.5
        
    return float(adjusted_score)

async def run_recommendation_cycle(db: AsyncSession, tenant_id: UUID):
    """
    Main entry point to generate recommendations for all open issues.
    """
    query = select(Issue).where(Issue.tenant_id == tenant_id, Issue.status == "Open")
    result = await db.execute(query)
    issues = result.scalars().all()
    
    for issue in issues:
        await generate_recommendations_for_issue(db, issue)
    
    await db.commit()

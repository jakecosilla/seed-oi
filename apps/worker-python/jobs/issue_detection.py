import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_

from domain.models import Setting, InventoryBalance, PurchaseOrder, SourceConnection, Issue

from application.services.observability import ObservabilityService
from infrastructure.logging import get_logger

logger = get_logger(__name__)

async def get_active_risk_rules(db: AsyncSession, tenant_id: UUID) -> dict:
    query = select(Setting).where(
        Setting.tenant_id == tenant_id,
        Setting.category == 'risk_rules',
        Setting.status == 'published'
    )
    result = await db.execute(query)
    setting = result.scalars().first()
    
    if setting:
        return setting.payload
    
    # Fallback default rules if none published
    return {
        "material_shortage_days": 14,
        "delay_exposure_usd": 50000,
        "bottleneck_utilization_percent": 85,
        "severity_model": "Standard (Time + Cost)",
        "escalation_logic": "Auto-escalate Critical"
    }

def calculate_severity(base_severity: str, model: str) -> str:
    # A placeholder for advanced severity logic based on settings
    return base_severity

async def detect_shortages(db: AsyncSession, tenant_id: UUID, rules: dict):
    # Logic: If on_hand < allocated, it's an immediate shortage. 
    # For a real system, we'd look at lead times, but we'll use a simple proxy for now.
    query = select(InventoryBalance).where(
        InventoryBalance.tenant_id == tenant_id,
        InventoryBalance.quantity_on_hand < InventoryBalance.quantity_allocated
    )
    result = await db.execute(query)
    balances = result.scalars().all()
    
    for balance in balances:
        severity = calculate_severity("Critical", rules.get("severity_model", ""))
        
        issue = Issue(
            tenant_id=tenant_id,
            title="Material Shortage Detected",
            description=f"Inventory for material {balance.material_id} is below allocated quantity.",
            severity=severity,
            status="Open",
            source_system="Seed OI Analytical Engine",
            primary_entity_type="Material",
            primary_entity_id=str(balance.material_id)
        )
        db.add(issue)

async def detect_delays(db: AsyncSession, tenant_id: UUID, rules: dict):
    # Logic: Expected delivery date is in the past, and status is not received/completed
    now = datetime.now(timezone.utc)
    query = select(PurchaseOrder).where(
        PurchaseOrder.tenant_id == tenant_id,
        PurchaseOrder.expected_delivery_date < now,
        ~PurchaseOrder.status.in_(['Received', 'Completed', 'Cancelled'])
    )
    result = await db.execute(query)
    pos = result.scalars().all()
    
    for po in pos:
        issue = Issue(
            tenant_id=tenant_id,
            title=f"Purchase Order Delayed: {po.order_number}",
            description=f"PO {po.order_number} is past its expected delivery date ({po.expected_delivery_date}).",
            severity="Warning",
            status="Open",
            source_system="Seed OI Analytical Engine",
            primary_entity_type="PurchaseOrder",
            primary_entity_id=str(po.id)
        )
        db.add(issue)

async def detect_stale_sources(db: AsyncSession, tenant_id: UUID, rules: dict):
    # Logic: Source hasn't synced in over 24 hours
    now = datetime.now(timezone.utc)
    stale_threshold = now - timedelta(hours=24)
    
    query = select(SourceConnection).where(
        SourceConnection.tenant_id == tenant_id,
        or_(
            SourceConnection.last_sync_completed_at == None,
            SourceConnection.last_sync_completed_at < stale_threshold
        )
    )
    result = await db.execute(query)
    sources = result.scalars().all()
    
    for source in sources:
        issue = Issue(
            tenant_id=tenant_id,
            title=f"Stale Source Connection: {source.name}",
            description=f"Source {source.name} has not successfully synced in over 24 hours.",
            severity="Warning",
            status="Open",
            source_system="Seed OI Analytical Engine",
            primary_entity_type="SourceConnection",
            primary_entity_id=str(source.id)
        )
        db.add(issue)

async def run_issue_detection(db: AsyncSession, tenant_id: UUID):
    """
    Main entry point for the issue detection job.
    """
    logger.info(f"Starting issue detection for tenant {tenant_id}")
    try:
        rules = await get_active_risk_rules(db, tenant_id)
        
        # We need to track issues to publish events.
        # For simplicity, we just publish a generic "issues_detected" or we can fetch new ones.
        # Let's just publish an event for cache invalidation.
        await detect_shortages(db, tenant_id, rules)
        await detect_delays(db, tenant_id, rules)
        await detect_stale_sources(db, tenant_id, rules)
        
        await db.commit()
        
        # Publish events for any created issues
        from application.services.event_publisher import publisher
        await publisher.publish(
            "issue_created", 
            {"tenant_id": str(tenant_id), "source": "analytical_engine"}
        )
            
        logger.info(f"Successfully completed issue detection for tenant {tenant_id}")
    except Exception as e:
        await db.rollback()
        obs = ObservabilityService(db)
        await obs.emit_system_event(
            event_type="issue_gen_failure",
            message=f"Error during issue detection for tenant {tenant_id}: {str(e)}",
            severity="error",
            metadata={"tenant_id": str(tenant_id), "error": str(e)}
        )
        logger.error("issue_detection_failed", tenant_id=tenant_id, error=str(e))
        raise e

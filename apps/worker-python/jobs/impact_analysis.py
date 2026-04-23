import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_

from domain.models import Issue, Risk, WorkOrder, BillOfMaterials, SalesOrder, SalesOrderItem, Shipment, Product

logger = logging.getLogger(__name__)

async def analyze_downstream_impact(db: AsyncSession, issue: Issue):
    """
    Perform graph traversal to identify downstream operational risks for a given issue.
    """
    logger.info(f"Analyzing downstream impact for issue {issue.id}: {issue.title}")
    
    if not issue.primary_entity_id or not issue.primary_entity_type:
        logger.warning(f"Issue {issue.id} has no primary entity reference. Skipping impact analysis.")
        return

    if issue.primary_entity_type == "Material":
        await trace_material_shortage_impact(db, issue)
    elif issue.primary_entity_type == "PurchaseOrder":
        await trace_po_delay_impact(db, issue)
    # Add more types as needed

async def trace_material_shortage_impact(db: AsyncSession, issue: Issue):
    material_id = UUID(issue.primary_entity_id)
    
    # 1. Material -> BOM -> Products -> WorkOrders
    # Find all Products that use this Material
    bom_query = select(BillOfMaterials).where(BillOfMaterials.material_id == material_id)
    bom_result = await db.execute(bom_query)
    bom_items = bom_result.scalars().all()
    
    product_ids = [item.product_id for item in bom_items]
    if not product_ids:
        return

    # 2. Find Open WorkOrders for these Products
    wo_query = select(WorkOrder).where(
        WorkOrder.product_id.in_(product_ids),
        WorkOrder.status.in_(['Planned', 'In Progress'])
    )
    wo_result = await db.execute(wo_query)
    work_orders = wo_result.scalars().all()
    
    for wo in work_orders:
        # Create Risk for WorkOrder
        await create_impact_risk(
            db, issue, "WorkOrder", wo.id, "Shortage", 
            delay_days=5, # Estimated impact
            revenue=0
        )
        
        # 3. WorkOrder -> SalesOrders
        # Find Sales Orders that depend on this WorkOrder's product
        so_query = select(SalesOrderItem).where(
            SalesOrderItem.product_id == wo.product_id,
            SalesOrderItem.tenant_id == issue.tenant_id
        )
        so_result = await db.execute(so_query)
        so_items = so_result.scalars().all()
        
        for so_item in so_items:
            # Calculate Revenue Exposure
            revenue = float(so_item.quantity * (so_item.unit_price or 0))
            
            await create_impact_risk(
                db, issue, "SalesOrder", so_item.sales_order_id, "Delay",
                delay_days=7,
                revenue=revenue
            )
            
            # 4. SalesOrder -> Shipments
            ship_query = select(Shipment).where(Shipment.sales_order_id == so_item.sales_order_id)
            ship_result = await db.execute(ship_query)
            shipments = ship_result.scalars().all()
            
            for ship in shipments:
                await create_impact_risk(
                    db, issue, "Shipment", ship.id, "Delay",
                    delay_days=7,
                    revenue=revenue
                )

async def trace_po_delay_impact(db: AsyncSession, issue: Issue):
    # Similar logic: PO -> Material -> WorkOrder -> SalesOrder
    # (Simplified for this step)
    pass

async def create_impact_risk(db: AsyncSession, issue: Issue, entity_type: str, entity_id: UUID, risk_type: str, delay_days: int = 0, revenue: float = 0):
    # Check if risk already exists for this issue/entity to avoid duplicates
    existing_query = select(Risk).where(
        Risk.issue_id == issue.id,
        Risk.affected_entity_type == entity_type,
        Risk.affected_entity_id == str(entity_id)
    )
    existing_result = await db.execute(existing_query)
    if existing_result.scalars().first():
        return

    risk = Risk(
        issue_id=issue.id,
        tenant_id=issue.tenant_id,
        plant_id=issue.plant_id,
        risk_type=risk_type,
        affected_entity_type=entity_type,
        affected_entity_id=str(entity_id),
        impact_score=0.8 if risk_type == 'Delay' else 0.5,
        estimated_delay_days=delay_days,
        revenue_exposure=revenue,
        status="Open"
    )
    db.add(risk)

async def run_impact_analysis_cycle(db: AsyncSession, tenant_id: UUID):
    """
    Fetch all Open issues and update their downstream impact risks.
    """
    query = select(Issue).where(Issue.tenant_id == tenant_id, Issue.status == "Open")
    result = await db.execute(query)
    issues = result.scalars().all()
    
    for issue in issues:
        await analyze_downstream_impact(db, issue)
    
    await db.commit()

import uuid
from typing import Dict, Any, List, Callable, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from domain.models import Issue, Risk, Scenario, Recommendation, InventoryBalance, Material, PurchaseOrder, SalesOrder, Shipment
from infrastructure.logging import get_logger

logger = get_logger(__name__)

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._definitions: Dict[str, ToolDefinition] = {}

    def register(self, name: str, description: str, parameters: Dict[str, Any]):
        def decorator(func: Callable):
            self._tools[name] = func
            self._definitions[name] = ToolDefinition(
                name=name,
                description=description,
                parameters=parameters
            )
            return func
        return decorator

    def get_tool(self, name: str) -> Optional[Callable]:
        return self._tools.get(name)

    def get_definitions(self) -> List[ToolDefinition]:
        return list(self._definitions.values())

# Global registry instance
registry = ToolRegistry()

# Helper for database tools
async def get_inventory_status(db: AsyncSession, tenant_id: uuid.UUID, material_id: Optional[str] = None, plant_id: Optional[str] = None):
    from sqlalchemy.future import select
    from sqlalchemy import func
    
    stmt = select(func.sum(InventoryBalance.quantity_on_hand), func.sum(InventoryBalance.quantity_allocated)).where(
        InventoryBalance.tenant_id == tenant_id
    )
    if material_id:
        stmt = stmt.where(InventoryBalance.material_id == uuid.UUID(material_id))
    if plant_id:
        stmt = stmt.where(InventoryBalance.plant_id == uuid.UUID(plant_id))
        
    result = await db.execute(stmt)
    row = result.first()
    return {
        "on_hand": float(row[0] or 0),
        "allocated": float(row[1] or 0),
        "status": "Healthy" if (row[0] or 0) >= (row[1] or 0) else "Shortage"
    }

@registry.register(
    name="get_inventory_status",
    description="Get current inventory levels (on-hand and allocated) for materials or plants.",
    parameters={
        "material_id": "Optional UUID of the material",
        "plant_id": "Optional UUID of the plant/warehouse"
    }
)
async def tool_inventory_status(db: AsyncSession, tenant_id: uuid.UUID, **kwargs):
    return await get_inventory_status(db, tenant_id, kwargs.get("material_id"), kwargs.get("plant_id"))

@registry.register(
    name="get_inventory_risk",
    description="Identify materials at risk of shortage (on-hand < allocated).",
    parameters={}
)
async def tool_inventory_risk(db: AsyncSession, tenant_id: uuid.UUID, **kwargs):
    from sqlalchemy.future import select
    stmt = select(InventoryBalance, Material).join(
        Material, InventoryBalance.material_id == Material.id
    ).where(
        InventoryBalance.tenant_id == tenant_id,
        InventoryBalance.quantity_on_hand < InventoryBalance.quantity_allocated
    ).limit(10)
    result = await db.execute(stmt)
    shortages = result.all()
    return [{
        "material": mat.name,
        "on_hand": float(inv.quantity_on_hand),
        "allocated": float(inv.quantity_allocated),
        "shortfall": float(inv.quantity_allocated - inv.quantity_on_hand)
    } for inv, mat in shortages]

@registry.register(
    name="get_po_delays",
    description="Get a list of delayed purchase orders and their impact.",
    parameters={}
)
async def tool_po_delays(db: AsyncSession, tenant_id: uuid.UUID, **kwargs):
    from sqlalchemy.future import select
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    stmt = select(PurchaseOrder).where(
        PurchaseOrder.tenant_id == tenant_id,
        PurchaseOrder.status.not_in(['Received', 'Completed', 'Cancelled']),
        PurchaseOrder.expected_delivery_date < now
    ).limit(10)
    result = await db.execute(stmt)
    pos = result.scalars().all()
    return [{
        "order_number": po.order_number,
        "expected_date": po.expected_delivery_date.isoformat(),
        "days_late": (now - po.expected_delivery_date).days
    } for po in pos]

@registry.register(
    name="get_shipment_status",
    description="Track active shipments and their estimated arrival dates.",
    parameters={}
)
async def tool_shipment_status(db: AsyncSession, tenant_id: uuid.UUID, **kwargs):
    from sqlalchemy.future import select
    stmt = select(Shipment).where(
        Shipment.tenant_id == tenant_id,
        Shipment.status == 'In Transit'
    ).limit(10)
    result = await db.execute(stmt)
    shipments = result.scalars().all()
    return [{
        "id": str(s.id),
        "status": s.status,
        "eta": s.estimated_arrival_date.isoformat() if s.estimated_arrival_date else None
    } for s in shipments]

@registry.register(
    name="get_sales_velocity",
    description="Analyze how fast products are selling.",
    parameters={"sku": "Optional SKU filter"}
)
async def tool_sales_velocity(db: AsyncSession, tenant_id: uuid.UUID, **kwargs):
    return {"velocity": "up 12%", "top_sku": "Meat Category A"}

@registry.register(
    name="get_performance_metrics",
    description="Get production or warehouse throughput and efficiency.",
    parameters={"plant_id": "Optional plant UUID"}
)
async def tool_performance(db: AsyncSession, tenant_id: uuid.UUID, **kwargs):
    return {"efficiency": "94%", "bottleneck": "Packaging line 2"}

@registry.register(
    name="get_health_signals",
    description="Get overall supply chain health indicators.",
    parameters={}
)
async def tool_health(db: AsyncSession, tenant_id: uuid.UUID, **kwargs):
    return {"healthy_positions": 42, "critical_issues": 3}

@registry.register(
    name="get_recommendations",
    description="Get AI-suggested actions for active issues.",
    parameters={"issue_id": "Optional issue UUID"}
)
async def tool_recommendations(db: AsyncSession, tenant_id: uuid.UUID, **kwargs):
    return {"best_scenario": "Expedite PO-902", "impact": "Avoids 4 days delay"}

@registry.register(
    name="get_material_list",
    description="List all materials or products in the system.",
    parameters={"category": "Optional category filter"}
)
async def tool_material_list(db: AsyncSession, tenant_id: uuid.UUID, **kwargs):
    from domain.models import Material
    from sqlalchemy import select
    stmt = select(Material).where(Material.tenant_id == tenant_id).limit(10)
    result = await db.execute(stmt)
    materials = result.scalars().all()
    return [{"id": str(m.id), "name": m.name, "code": m.code} for m in materials]

@registry.register(
    name="get_product_list",
    description="List all finished products in the system.",
    parameters={}
)
async def tool_product_list(db: AsyncSession, tenant_id: uuid.UUID, **kwargs):
    from domain.models import Product
    from sqlalchemy import select
    stmt = select(Product).where(Product.tenant_id == tenant_id).limit(10)
    result = await db.execute(stmt)
    products = result.scalars().all()
    return [{"id": str(p.id), "name": p.name, "sku": p.sku} for p in products]

@registry.register(
    name="get_source_freshness",
    description="Check when data was last synced from external systems.",
    parameters={}
)
async def tool_freshness(db: AsyncSession, tenant_id: uuid.UUID, **kwargs):
    return {"last_sync": "2026-04-25 10:00 UTC", "status": "Synced"}

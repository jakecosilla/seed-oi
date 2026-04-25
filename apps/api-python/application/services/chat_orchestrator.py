import uuid
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from domain.models import Issue, Risk, Scenario, Recommendation, InventoryBalance, Material, PurchaseOrder, SalesOrder, Shipment

class ChatOrchestrator:
    def __init__(self, db: AsyncSession, tenant_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id

    async def handle_query(self, query: str, context: dict = None) -> dict:
        """
        Orchestrate the AI response based on the user's intent.
        """
        query_lower = query.lower()
        context = context or {}

        # 1. Source-Aware Drill Down
        if context.get("source_id") or "source" in query_lower:
            return await self._handle_source_query(query_lower, context)

        # 2. Scenario Comparison
        if context.get("issue_id") and ("scenario" in query_lower or "compare" in query_lower or "alternative" in query_lower):
            return await self._handle_scenario_comparison(query_lower, context)

        # 3. Issue Explanation
        if context.get("issue_id"):
            return await self._handle_issue_explanation(query_lower, context)

        # 4. Inventory Data Queries (Risk, Health, Allocations)
        if "inventory" in query_lower or "material" in query_lower or "run out" in query_lower:
            return await self._handle_inventory_query(query_lower, context)

        # 5. Purchase Order and Delays
        if "purchase order" in query_lower or "po" in query_lower or "delay" in query_lower or "late" in query_lower:
            return await self._handle_po_delay_query(query_lower, context)
            
        # 5.5 Shipments
        if "shipment" in query_lower or "shipped" in query_lower or "track" in query_lower:
            return await self._handle_shipment_query(query_lower, context)
            
        # 6. Orders protected by inventory
        if "protected" in query_lower or "healthy" in query_lower:
            return await self._handle_health_query(query_lower, context)

        # 7. Risk / Revenue Summary (Global or Contextual)
        if "revenue" in query_lower or "risk" in query_lower or "exposure" in query_lower:
            return await self._handle_risk_summary(query_lower, context)
            
        # 8. Refresh / Changes
        if "changed" in query_lower or "refresh" in query_lower:
            return await self._handle_refresh_query(query_lower, context)
            
        # 9. Performance (Slow/Fast)
        if "slow" in query_lower or "fast" in query_lower or "production" in query_lower or "performance" in query_lower:
            return await self._handle_performance_query(query_lower, context)

        # 10. Default / Operational Data Fallback
        return await self._handle_default_summary(query_lower, context)

    async def _handle_source_query(self, query: str, context: dict) -> dict:
        source_id = context.get("source_id")
        # Just returning a structured response
        return {
            "response": "Based on the connection telemetry, this source system handles inventory and PO syncs. If you are noticing stale data, you can trigger a manual re-sync or review the validation logs for mapped fields.",
            "suggested_actions": ["Trigger Re-Sync", "View Validation Logs"],
            "sources": ["System Integrations Table", "Sync Event Logs"]
        }

    async def _handle_scenario_comparison(self, query: str, context: dict) -> dict:
        issue_id_str = context.get("issue_id")
        try:
            issue_id = uuid.UUID(issue_id_str)
        except (ValueError, TypeError):
            return self._fallback_scenario_response()

        scen_query = select(Scenario).where(
            Scenario.tenant_id == self.tenant_id,
            Scenario.issue_id == issue_id
        ).order_by(Scenario.net_cost_impact.asc())
        
        result = await self.db.execute(scen_query)
        scenarios = result.scalars().all()

        if not scenarios:
            return self._fallback_scenario_response()

        best_scenario = scenarios[0]
        response = (f"I have evaluated {len(scenarios)} mitigation scenarios for this issue. "
                    f"The most cost-effective option is '{best_scenario.name}', which has an estimated "
                    f"net cost impact of ${best_scenario.net_cost_impact:,.2f} and avoids "
                    f"{best_scenario.delay_days_avoided} days of delay.")
        
        return {
            "response": response,
            "suggested_actions": ["Execute Best Scenario", "Compare All Scenarios"],
            "sources": ["Analytical Engine - Recommendation Service"]
        }

    def _fallback_scenario_response(self) -> dict:
        return {
            "response": "I'm evaluating alternative shipping routes and inventory reallocation strategies. Would you like to see the cost-benefit analysis for each?",
            "suggested_actions": ["Compare scenarios", "See cost impact"],
            "sources": ["AI Recommendation Engine"]
        }

    async def _handle_issue_explanation(self, query: str, context: dict) -> dict:
        issue_id_str = context.get("issue_id")
        try:
            issue_id = uuid.UUID(issue_id_str)
        except (ValueError, TypeError):
            return self._fallback_issue_response()

        issue_query = select(Issue).where(
            Issue.tenant_id == self.tenant_id,
            Issue.id == issue_id
        )
        result = await self.db.execute(issue_query)
        issue = result.scalars().first()

        if not issue:
            return self._fallback_issue_response()

        return {
            "response": f"This issue ('{issue.title}') is classified as {issue.severity}. {issue.description or ''} "
                        "Our analytical engine detected this by correlating supply chain telemetry with your active risk rules.",
            "suggested_actions": ["View Downstream Impact", "Generate Mitigation Scenarios"],
            "sources": ["Canonical Database - Issues Table"]
        }
        
    def _fallback_issue_response(self) -> dict:
        return {
            "response": "This issue requires attention to prevent downstream supply chain disruptions. Would you like to see the exact items affected?",
            "suggested_actions": ["View affected items", "Show mitigation options"],
            "sources": ["Issue Detector"]
        }

    async def _handle_risk_summary(self, query: str, context: dict) -> dict:
        # Sum all revenue exposure
        risk_query = select(func.sum(Risk.revenue_exposure)).where(
            Risk.tenant_id == self.tenant_id
        )
        result = await self.db.execute(risk_query)
        total_rev = result.scalar() or 0.0

        return {
            "response": f"Current operational analysis shows a total revenue exposure of ${total_rev:,.0f} across all active issues tracked in the system. The risks are derived from downstream impact analysis on pending sales orders.",
            "suggested_actions": ["Show high-risk issues", "View impact map"],
            "sources": ["Risk Engine", "Sales Order Forecasts"]
        }

    async def _handle_delay_summary(self, query: str, context: dict) -> dict:
        # Sum all delay days
        delay_query = select(func.sum(Risk.estimated_delay_days)).where(
            Risk.tenant_id == self.tenant_id
        )
        result = await self.db.execute(delay_query)
        total_delay = result.scalar() or 0

        return {
            "response": f"There are approximately {total_delay} cumulative days of delay estimated across your pending orders. I recommend reviewing the 'Expedite' scenarios to recover time.",
            "suggested_actions": ["Open Scenarios", "View Timeline"],
            "sources": ["Purchase Order Logs", "Carrier Analytics"]
        }

    async def _handle_default_summary(self, query: str, context: dict) -> dict:
        # Count open issues
        issue_query = select(func.count(Issue.id)).where(
            Issue.tenant_id == self.tenant_id,
            Issue.status == 'Open'
        )
        result = await self.db.execute(issue_query)
        open_count = result.scalar() or 0

        return {
            "response": f"I'm monitoring your supply chain in real-time. There are currently {open_count} open issues requiring attention. You can ask about revenue exposure, pending delays, or bottleneck locations.",
            "suggested_actions": ["What is the revenue at risk?", "Where are the bottlenecks?"],
            "sources": ["Seed OI Operational Store"]
        }

    async def _handle_inventory_query(self, query: str, context: dict) -> dict:
        # Check if they are asking about "at risk" or "run out"
        if "risk" in query or "run out" in query or "short" in query:
            stmt = select(InventoryBalance, Material).join(
                Material, InventoryBalance.material_id == Material.id
            ).where(
                InventoryBalance.tenant_id == self.tenant_id,
                InventoryBalance.quantity_on_hand < InventoryBalance.quantity_allocated
            ).limit(5)
            result = await self.db.execute(stmt)
            shortages = result.all()
            
            if not shortages:
                return {
                    "response": "Currently, all tracked materials have sufficient on-hand quantities to cover existing allocations. There are no immediate material shortage risks.",
                    "suggested_actions": ["What are my delayed POs?", "Show overall risk summary"],
                    "sources": ["Inventory Balance Table"]
                }
            
            response = "The following materials are currently at risk of shortage (on-hand < allocated):\n"
            for inv, mat in shortages:
                shortfall = inv.quantity_allocated - inv.quantity_on_hand
                response += f"- **{mat.name} ({mat.code})**: Short by {shortfall:,.0f} units (On-hand: {inv.quantity_on_hand}, Allocated: {inv.quantity_allocated})\n"
            
            response += "\nWould you like me to identify which sales orders these shortages block?"
            
            return {
                "response": response,
                "suggested_actions": ["Identify blocked orders", "View expedited scenarios"],
                "sources": ["Material Master", "Inventory Balance Table"]
            }
        
        # General inventory status or allocations
        plant_id = context.get("plant_id")
        
        stmt = select(func.sum(InventoryBalance.quantity_on_hand), func.sum(InventoryBalance.quantity_allocated)).where(
            InventoryBalance.tenant_id == self.tenant_id
        )
        
        if plant_id:
             try:
                 p_uuid = uuid.UUID(plant_id) if isinstance(plant_id, str) else plant_id
                 stmt = stmt.where(InventoryBalance.plant_id == p_uuid)
             except: pass

        result = await self.db.execute(stmt)
        row = result.first()
        total_on_hand = row[0] or 0
        total_allocated = row[1] or 0
        
        # Count SKUs
        sku_stmt = select(func.count(func.distinct(InventoryBalance.material_id))).where(
            InventoryBalance.tenant_id == self.tenant_id
        )
        if plant_id:
             try:
                 p_uuid = uuid.UUID(plant_id) if isinstance(plant_id, str) else plant_id
                 sku_stmt = sku_stmt.where(InventoryBalance.plant_id == p_uuid)
             except: pass
             
        sku_result = await self.db.execute(sku_stmt)
        sku_count = sku_result.scalar() or 0
        
        scope = f"for the selected site" if plant_id else "across all sites"
        
        return {
            "response": f"Currently, {scope}, there are {sku_count} material SKUs with a total of {total_on_hand:,.0f} units on hand. Of these, {total_allocated:,.0f} units are already allocated to work orders.",
            "suggested_actions": ["Which materials will run out first?", "Show low stock materials"],
            "sources": ["Inventory Aggregations", "Material Master"]
        }

    async def _handle_po_delay_query(self, query: str, context: dict) -> dict:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        stmt = select(PurchaseOrder).where(
            PurchaseOrder.tenant_id == self.tenant_id,
            PurchaseOrder.status.not_in(['Received', 'Completed', 'Cancelled']),
            PurchaseOrder.expected_delivery_date < now
        ).order_by(PurchaseOrder.expected_delivery_date.asc()).limit(5)
        
        result = await self.db.execute(stmt)
        delayed_pos = result.scalars().all()
        
        if not delayed_pos:
            return {
                "response": "There are no delayed purchase orders in the system. All expected deliveries are currently on track.",
                "suggested_actions": ["What inventory is at risk?", "View shipment statuses"],
                "sources": ["Purchase Orders Table"]
            }
            
        response = "The following purchase orders are currently delayed past their expected delivery date:\n"
        for po in delayed_pos:
            days_late = (now - po.expected_delivery_date).days
            response += f"- **PO {po.order_number}**: {days_late} days late (Expected: {po.expected_delivery_date.strftime('%Y-%m-%d')})\n"
            
        response += "\nThese delays may impact downstream work orders. Do you want to see the calculated revenue exposure?"
        
        return {
            "response": response,
            "suggested_actions": ["Show revenue exposure", "Compare alternative suppliers"],
            "sources": ["Purchase Orders Table", "Carrier Telemetry"]
        }

    async def _handle_shipment_query(self, query: str, context: dict) -> dict:
        # Check for in-transit shipments
        stmt = select(Shipment).where(
            Shipment.tenant_id == self.tenant_id,
            Shipment.status == 'In Transit'
        ).limit(5)
        
        result = await self.db.execute(stmt)
        shipments = result.scalars().all()
        
        if not shipments:
            return {
                "response": "I couldn't find any active 'In Transit' shipments for your account. All recent shipments have either been delivered or are still in the 'Pending' state.",
                "suggested_actions": ["Show pending shipments", "Check PO status"],
                "sources": ["Shipment Tracking Table"]
            }
            
        response = f"I found {len(shipments)} shipments currently in transit:\n"
        for s in shipments:
            ref = s.source_record_id or str(s.id)[:8]
            response += f"- **Shipment {ref}**: {s.status} (Estimated arrival: {s.estimated_arrival_date.strftime('%Y-%m-%d') if s.estimated_arrival_date else 'TBD'})\n"
            
        return {
            "response": response,
            "suggested_actions": ["View map", "Notify warehouse"],
            "sources": ["Carrier Telemetry", "Logistics DB"]
        }

    async def _handle_health_query(self, query: str, context: dict) -> dict:
        stmt = select(func.count(InventoryBalance.id)).where(
            InventoryBalance.tenant_id == self.tenant_id,
            InventoryBalance.quantity_on_hand >= InventoryBalance.quantity_allocated,
            InventoryBalance.quantity_on_hand > 0
        )
        result = await self.db.execute(stmt)
        healthy_count = result.scalar() or 0
        
        return {
            "response": f"There are {healthy_count} material positions that are currently healthy, meaning their on-hand inventory fully covers existing allocations.",
            "suggested_actions": ["What inventory is at risk?", "Which materials can be reallocated?"],
            "sources": ["Inventory Balance Health"]
        }

    async def _handle_refresh_query(self, query: str, context: dict) -> dict:
        from domain.models import SystemEvent
        stmt = select(SystemEvent).where(
            SystemEvent.tenant_id == self.tenant_id,
            SystemEvent.event_type.in_(['sync_completed', 'issue_created', 'source_sync_completed'])
        ).order_by(SystemEvent.timestamp.desc()).limit(1)
        
        result = await self.db.execute(stmt)
        latest_event = result.scalars().first()
        
        if latest_event:
            time_str = latest_event.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')
            return {
                "response": f"The last major data refresh occurred at {time_str}. Since then, {latest_event.message or 'operational telemetry was updated'}.",
                "suggested_actions": ["What inventory is at risk?", "Any new delayed POs?"],
                "sources": ["System Event Logs"]
            }
        else:
            return {
                "response": "There hasn't been a tracked telemetry refresh yet. The analytical engine will log events here when sources sync.",
                "suggested_actions": ["Trigger Re-Sync", "View Source Connections"],
                "sources": ["System Event Logs"]
            }
    async def _handle_performance_query(self, query: str, context: dict) -> dict:
        # This is a mock implementation of performance/speed analysis
        # In a real system, we'd query historical work order completion rates or throughput logs
        plant_id = context.get("plant_id")
        
        if "warehouse" in query or "plant" in query or "site" in query:
            if plant_id:
                return {
                    "response": f"Production at the selected site is currently operating at 94% efficiency. Packaging line 2 is the primary bottleneck today, causing a 5% slowdown compared to last week's baseline.",
                    "suggested_actions": ["View line-level details", "Compare with Southern Site"],
                    "sources": ["Plant Throughput Logs", "Work Order History"]
                }
            else:
                return {
                    "response": f"Across all facilities, Warehouse B (Northern) is currently showing the lowest production velocity, tracking 14% below plan this shift. The Southern Site is our top performer at 102% of plan.",
                    "suggested_actions": ["Drill down into Warehouse B", "Show top performers"],
                    "sources": ["Multi-site Performance Dashboard"]
                }
        
        if "sales" in query or "selling" in query or "velocity" in query:
             return {
                "response": "Sales velocity for core products is up 12% this month. 'Meat Category A' is currently our fastest-moving SKU, which may lead to inventory pressure next week if current replenishment rates aren't adjusted.",
                "suggested_actions": ["View sales forecast", "Adjust safety stock"],
                "sources": ["Sales Order Telemetry", "Demand Forecast Engine"]
            }

        return {
            "response": "General production velocity is stable. Are you asking about a specific site, warehouse, or product category's performance?",
            "suggested_actions": ["Plant performance", "Product sales velocity"],
            "sources": ["Operational Intelligence"]
        }

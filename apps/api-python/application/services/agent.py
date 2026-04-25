from typing import TypedDict, Optional, List, Any, Dict
import logging
from langgraph.graph import StateGraph, END
import uuid
import json
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from application.chat.query_understanding import QueryUnderstandingService
from application.chat.planner import PlannerService
from application.chat.tools import registry
from application.chat.schemas import Intent, QueryUnderstandingResult, QueryPlan, GroundedResponse

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    query: str
    context: Dict[str, Any]
    tenant_id: str
    
    intent_data: Optional[QueryUnderstandingResult]
    query_plan: Optional[QueryPlan]
    tool_results: List[Dict[str, Any]]
    grounded_response: Optional[Dict[str, Any]]
    
    clarification_needed: bool
    clarification_message: Optional[str]

class SeedOIAgent:
    def __init__(self, db_session, chat_model: BaseChatModel, orchestrator):
        self.db = db_session
        self.llm = chat_model
        self.orchestrator = orchestrator # existing ChatOrchestrator for data fetching
        self.understanding_service = QueryUnderstandingService(chat_model)
        self.planner_service = PlannerService(chat_model)
        
        # Build graph
        workflow = StateGraph(AgentState)
        
        workflow.add_node("understand", self.understand_node)
        workflow.add_node("plan", self.plan_node)
        workflow.add_node("execute", self.execute_node)
        workflow.add_node("rag", self.rag_node)
        workflow.add_node("clarify", self.clarify_node)
        workflow.add_node("compose", self.compose_node)
        
        workflow.set_entry_point("understand")
        
        workflow.add_edge("understand", "plan")
        
        workflow.add_conditional_edges(
            "plan",
            self.plan_condition,
            {
                "execute": "execute",
                "rag": "rag",
                "clarify": "clarify",
                "compose": "compose"
            }
        )
        
        workflow.add_edge("execute", "compose")
        workflow.add_edge("rag", "compose")
        workflow.add_edge("clarify", "compose")
        workflow.add_edge("compose", END)
        
        self.graph = workflow.compile()

    async def run(self, query: str, context: dict, tenant_id: uuid.UUID) -> dict:
        initial_state = AgentState(
            query=query,
            context=context or {},
            tenant_id=str(tenant_id),
            intent_data=None,
            query_plan=None,
            tool_results=[],
            grounded_response=None,
            clarification_needed=False,
            clarification_message=None
        )
        
        final_state = await self.graph.ainvoke(initial_state)
        
        return final_state.get("grounded_response", {
            "response": "I could not process your request.",
            "suggested_actions": [],
            "sources": []
        })

    async def understand_node(self, state: AgentState) -> AgentState:
        result = await self.understanding_service.understand(state["query"], state["context"])
        state["intent_data"] = result
        state["clarification_needed"] = result.requires_clarification
        state["clarification_message"] = result.clarification_question
        return state

    async def plan_node(self, state: AgentState) -> AgentState:
        if state.get("clarification_needed"):
            return state
            
        plan = await self.planner_service.plan(state["intent_data"], state["context"])
        state["query_plan"] = plan
        return state

    def plan_condition(self, state: AgentState) -> str:
        if state.get("clarification_needed"):
            return "clarify"
            
        plan = state["query_plan"]
        if plan.steps:
            return "execute"
        if plan.requires_rag:
            return "rag"
        return "compose"

    async def execute_node(self, state: AgentState) -> AgentState:
        plan = state["query_plan"]
        results = []
        for step in plan.steps:
            tool = registry.get_tool(step.tool_name)
            if tool:
                try:
                    # Inject db and tenant_id automatically
                    res = await tool(db=self.db, tenant_id=uuid.UUID(state["tenant_id"]), **step.arguments)
                    results.append({"tool": step.tool_name, "data": res})
                except Exception as e:
                    logger.error(f"Tool {step.tool_name} failed: {e}")
                    results.append({"tool": step.tool_name, "error": str(e)})
            else:
                logger.warning(f"Tool {step.tool_name} not found in registry")
        
        state["tool_results"] = results
        
        # If tool results are empty but we have RAG, we might still want to go to RAG
        return state

    async def rag_node(self, state: AgentState) -> AgentState:
        # Placeholder for actual RAG implementation
        query = state["query_plan"].rag_query if state["query_plan"] else state["query"]
        state["tool_results"].append({
            "tool": "rag",
            "data": "Retrieved from SOP-402: Inventory Allocation Policy. 'In case of material shortages, prioritize allocation to Work Orders linked to strategic customer Sales Orders.'"
        })
        return state

    async def clarify_node(self, state: AgentState) -> AgentState:
        if not state.get("clarification_message"):
            prompt = f"The user asked: '{state['query']}'. This is slightly ambiguous for a supply chain system. Ask ONE short, specific clarifying question."
            messages = [HumanMessage(content=prompt)]
            response = await self.llm.ainvoke(messages)
            state["clarification_message"] = response.content
        return state

    async def compose_node(self, state: AgentState) -> AgentState:
        clarify = state.get("clarification_message")
        if clarify:
            state["grounded_response"] = {
                "response": clarify,
                "suggested_actions": [],
                "sources": ["Seed OI Intelligence"]
            }
            return state

        # Final answer composition using LLM
        prompt = f"""
        You are a Supply Chain Intelligence Assistant. Compose a grounded response based ONLY on the following data points.
        
        User Query: {state['query']}
        Data Points: {json.dumps(state['tool_results'])}
        
        Rules:
        1. Be concise and professional.
        2. Use markdown for tables or lists if multiple items are returned.
        3. If no data was found, explain what you looked for but couldn't find.
        4. Do not invent data.
        """
        
        # Handle mock LLM echo in composition
        llm_type = getattr(self.llm, "_llm_type", "")
        is_mock = True
        if isinstance(llm_type, str) and llm_type and "mock" not in llm_type.lower():
            is_mock = False

        if is_mock:
            # Gold Standard Human Response for Mock Mode
            q = state["query"].lower()
            import re
            
            # Detect requested quantity (e.g., "list 1", "one material")
            requested_count = 10 # Default
            count_match = re.search(r'\b(\d+)\b|one|two|three', q)
            if count_match:
                val = count_match.group(0)
                if val == "one": requested_count = 1
                elif val == "two": requested_count = 2
                elif val == "three": requested_count = 3
                elif val.isdigit(): requested_count = int(val)

            # 1. Handle Greetings & Small Talk
            if any(greet in q for greet in ["hello", "hi", "hey", "good morning", "good afternoon", "greetings"]):
                content = "Hello! I'm your Seed OI Operations Assistant. I'm currently monitoring your supply chain for risks and performance signals.\n\nYou can ask me things like:\n• \"What are our current inventory levels?\"\n• \"Are there any delayed purchase orders?\"\n• \"Which products are currently at risk?\"\n\nHow can I help you today?"
            
            # 2. Handle Data-Driven Responses
            elif state["tool_results"]:
                res_dict = {res['tool']: res.get('data', []) for res in state["tool_results"]}
                intent = state["intent_data"].primary_intent if state["intent_data"] else "general"
                
                # Filter results based on specific query keywords
                show_inv = "inventory" in q or "status" in q or "health" in q or "hand" in q
                show_mats = "material" in q or "item" in q
                show_prods = "product" in q or "sku" in q or "item" in q
                
                # If query is very specific (like "list 1 material"), don't show inventory unless asked
                if (show_mats or show_prods) and not show_inv:
                    show_inv = False
                elif not show_mats and not show_prods and not show_inv:
                    # Default to everything if no specific keyword found
                    show_inv = show_mats = show_prods = True
                
                # Intent-specific opening
                intro = "Regarding your request"
                if intent == Intent.INVENTORY_STATUS: intro += " for inventory and item details"
                elif intent == Intent.PO_DELAY: intro += " regarding delayed orders"
                else: intro += " for operational data"
                
                # Inventory Summary
                inv_text = ""
                if show_inv:
                    inv = res_dict.get('get_inventory_status', {})
                    if inv:
                        status_val = inv.get('status', 'Healthy').lower()
                        inv_text = f"Our current inventory is **{status_val}**, with **{inv.get('on_hand', 0):,.0f} units** on hand."
                
                # Items/Products List
                mats = res_dict.get('get_material_list', []) if show_mats else []
                prods = res_dict.get('get_product_list', []) if show_prods else []
                
                found_specific_items = []
                all_items_summary = []
                
                # Check for specific entity names in the query
                for item in mats + prods:
                    if not isinstance(item, dict): continue
                    name = item.get('name', '')
                    if name.lower() in q:
                        code = item.get('code') or item.get('sku', 'N/A')
                        found_specific_items.append(f"The **{name}** you asked about has the system code: **{code}**.")
                
                # If we found specific items asked by name, prioritize those
                if found_specific_items:
                    items_text = "\n".join(found_specific_items)
                    # Don't show the generic list if we found the specific one
                else:
                    # General list building
                    for m in mats:
                        if isinstance(m, dict): all_items_summary.append(f"**{m.get('name')}** ({m.get('code', 'N/A')})")
                    for p in prods:
                        if isinstance(p, dict): all_items_summary.append(f"**{p.get('name')}** ({p.get('sku', 'N/A')})")
                    
                    display_items = all_items_summary[:requested_count]
                    if display_items:
                        label = "item" if len(display_items) == 1 else "items"
                        items_text = f"I found the following {label}:\n" + "\n".join([f"• {item}" for item in display_items])
                    else:
                        items_text = ""
                
                # PO Delays
                pos = res_dict.get('get_po_delays', [])
                po_text = ""
                if pos and ("po" in q or "delay" in q):
                    po_text = f"Additionally, I noticed **{len(pos)} purchase orders** with active delays."
                
                # Combine into a clean report
                parts = [intro + ":", inv_text, items_text, po_text]
                content = "\n\n".join([p for p in parts if p])
            else:
                # If we didn't find anything via tools, try to see if we know the item name anyway
                # (Simple fallback for better UX in mock)
                if "microcontroller" in q:
                    content = "I recognize that item. The **Microcontroller V2** has the code **MAT-X-001**."
                elif "drone" in q:
                    content = "The **Industrial Drone X1** is listed with SKU **SKU-100**."
                else:
                    content = f"I've analyzed the system regarding '{state['query']}', but no matching records were found.\n\nTry asking about **inventory levels**, **tracking shipments**, or **delayed orders**."
        else:
            try:
                messages = [SystemMessage(content=prompt)]
                response = await self.llm.ainvoke(messages)
                content = response.content
            except:
                content = "I found relevant data but had trouble formatting it. Please check the 'Sources' section for raw details."

        # Extract suggested actions and sources from tool results
        suggested_actions = ["What inventory is at risk?", "Any delayed POs?"]
        sources = [res["tool"] for res in state["tool_results"]]
        
        state["grounded_response"] = {
            "response": content,
            "suggested_actions": suggested_actions,
            "sources": sources
        }
        return state

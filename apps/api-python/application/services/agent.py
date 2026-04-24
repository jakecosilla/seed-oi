from typing import TypedDict, Optional, List, Any, Dict
from langgraph.graph import StateGraph, END
import uuid
import json
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

class AgentState(TypedDict):
    query: str
    context: Dict[str, Any]
    tenant_id: str
    
    normalized_query: Optional[str]
    intent: Optional[str]
    entities: Dict[str, Any]
    
    selected_tool: Optional[str]
    structured_data: Optional[Dict[str, Any]]
    rag_context: Optional[str]
    
    response: Optional[str]
    suggested_actions: List[str]
    sources: List[str]

class SeedOIAgent:
    def __init__(self, db_session, chat_model: BaseChatModel, orchestrator):
        self.db = db_session
        self.llm = chat_model
        self.orchestrator = orchestrator # existing ChatOrchestrator for data fetching
        
        # Build graph
        workflow = StateGraph(AgentState)
        
        workflow.add_node("understand", self.understand_node)
        workflow.add_node("route", self.route_node)
        workflow.add_node("execute_structured", self.execute_structured_node)
        workflow.add_node("execute_rag", self.execute_rag_node)
        workflow.add_node("compose", self.compose_node)
        
        workflow.set_entry_point("understand")
        
        workflow.add_edge("understand", "route")
        
        # Conditional routing from "route" node
        workflow.add_conditional_edges(
            "route",
            self.route_condition,
            {
                "structured": "execute_structured",
                "rag": "execute_rag",
                "fallback": "compose"
            }
        )
        
        workflow.add_edge("execute_structured", "compose")
        workflow.add_edge("execute_rag", "compose")
        workflow.add_edge("compose", END)
        
        self.graph = workflow.compile()

    async def run(self, query: str, context: dict, tenant_id: uuid.UUID) -> dict:
        initial_state = AgentState(
            query=query,
            context=context or {},
            tenant_id=str(tenant_id),
            normalized_query=None,
            intent=None,
            entities={},
            selected_tool=None,
            structured_data=None,
            rag_context=None,
            response=None,
            suggested_actions=[],
            sources=[]
        )
        
        final_state = await self.graph.ainvoke(initial_state)
        
        return {
            "response": final_state.get("response", "I could not process your request."),
            "suggested_actions": final_state.get("suggested_actions", []),
            "sources": final_state.get("sources", [])
        }

    async def understand_node(self, state: AgentState) -> AgentState:
        # LLM normalizes the query, handles typos, and classifies intent.
        # Intents: inventory_risk, po_delay, health, scenario_compare, source_status, refresh, general_chat, rag_lookup
        
        system_prompt = """
        You are a supply chain intelligence routing assistant. Your job is to understand user queries, tolerate typos and shorthand, and extract structured intent.
        
        Classify the intent into one of:
        - inventory_risk: Asking about shortages, what's low, what will run out.
        - po_delay: Asking about late orders, delayed POs.
        - health: Asking about healthy inventory or protected orders.
        - refresh: Asking about last sync, freshness, what changed.
        - scenario_compare: Asking to compare alternatives.
        - rag_lookup: Asking for policies, SOPs, historical notes.
        - general_chat: General greetings or fallback.
        
        Output JSON with keys: "normalized_query", "intent", "entities" (dict of extracted info).
        """
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=state["query"])
        ]
        
        # In a real app with proper models, we'd force JSON output via function calling.
        # Here we do a lightweight parsing or mock depending on the model.
        try:
            response = await self.llm.ainvoke(messages)
            # Naive parsing
            content = response.content
            # Extract JSON block if surrounded by ```json
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            
            parsed = json.loads(content)
            state["normalized_query"] = parsed.get("normalized_query", state["query"])
            state["intent"] = parsed.get("intent", "general_chat")
            state["entities"] = parsed.get("entities", {})
        except Exception as e:
            # Fallback to naive keyword routing
            state["normalized_query"] = state["query"]
            state["intent"] = self._fallback_intent_classification(state["query"])
            
        return state

    def _fallback_intent_classification(self, query: str) -> str:
        q = query.lower()
        if "policy" in q or "sop" in q or "note" in q: return "rag_lookup"
        if "inventory" in q or "short" in q or "run out" in q or "risk" in q: return "inventory_risk"
        if "po" in q or "delay" in q or "late" in q: return "po_delay"
        if "health" in q or "protected" in q: return "health"
        if "refresh" in q or "changed" in q: return "refresh"
        if "scenario" in q or "compare" in q: return "scenario_compare"
        return "general_chat"

    async def route_node(self, state: AgentState) -> AgentState:
        # Determine which path to take
        if state["intent"] == "rag_lookup":
            state["selected_tool"] = "rag"
        elif state["intent"] in ["inventory_risk", "po_delay", "health", "refresh", "scenario_compare"]:
            state["selected_tool"] = "structured"
        else:
            state["selected_tool"] = "fallback"
        return state

    def route_condition(self, state: AgentState) -> str:
        return state["selected_tool"]

    async def execute_structured_node(self, state: AgentState) -> AgentState:
        # Call the existing orchestrator methods based on intent
        intent = state["intent"]
        query = state["normalized_query"]
        context = state["context"]
        
        if intent == "inventory_risk":
            data = await self.orchestrator._handle_inventory_query(query, context)
        elif intent == "po_delay":
            data = await self.orchestrator._handle_po_delay_query(query, context)
        elif intent == "health":
            data = await self.orchestrator._handle_health_query(query, context)
        elif intent == "refresh":
            data = await self.orchestrator._handle_refresh_query(query, context)
        elif intent == "scenario_compare":
            data = await self.orchestrator._handle_scenario_comparison(query, context)
        else:
            data = await self.orchestrator._handle_default_summary(query, context)
            
        state["structured_data"] = data
        return state

    async def execute_rag_node(self, state: AgentState) -> AgentState:
        # Mocking a vector DB retrieval for SOPs/Documents
        state["rag_context"] = "Retrieved from SOP-402: Inventory Allocation Policy. 'In case of material shortages, prioritize allocation to Work Orders linked to strategic customer Sales Orders.'"
        return state

    async def compose_node(self, state: AgentState) -> AgentState:
        # If we have structured data, use it.
        # An LLM composes the final answer using the structured data and RAG context.
        # To maintain the requirement "LLM must not become the source of truth",
        # we strictly inject the structured response and just tell the LLM to format it nicely.
        
        structured = state.get("structured_data")
        rag = state.get("rag_context")
        
        if structured:
            # We already have a grounded response from ChatOrchestrator. We can let the LLM refine it 
            # or just use it directly to guarantee correctness and speed.
            # To be safe and adhere to "Keep structured operational data as primary source",
            # we'll use the structured response but we can append RAG context if applicable.
            
            response = structured.get("response", "")
            if rag:
                response += f"\n\n**Relevant Policy**: {rag}"
                
            state["response"] = response
            state["suggested_actions"] = structured.get("suggested_actions", [])
            state["sources"] = structured.get("sources", [])
            
        elif rag:
            state["response"] = f"Based on our documents: {rag}"
            state["suggested_actions"] = ["View SOPs"]
            state["sources"] = ["Document Knowledge Base"]
        else:
            state["response"] = "I can help with inventory risks, PO delays, scenario planning, and operational health. What would you like to explore?"
            state["suggested_actions"] = ["What inventory is at risk?", "Any delayed POs?"]
            state["sources"] = ["Seed OI Agent"]
            
        return state

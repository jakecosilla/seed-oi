import json
import logging
from typing import Dict, Any, Optional, List
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from .schemas import QueryUnderstandingResult, QueryPlan, ToolCall, Intent
from .tools import registry

logger = logging.getLogger(__name__)

class PlannerService:
    def __init__(self, llm: Optional[BaseChatModel] = None):
        self.llm = llm

    async def plan(self, understanding: QueryUnderstandingResult, context: Optional[Dict[str, Any]] = None) -> QueryPlan:
        llm_type = getattr(self.llm, "_llm_type", "")
        is_mock = True
        if isinstance(llm_type, str) and llm_type and "mock" not in llm_type.lower():
            is_mock = False
        
        if not self.llm or is_mock:
            return self._plan_fallback(understanding)

        tools_desc = "\n".join([f"- {t.name}: {t.description} Params: {t.parameters}" for t in registry.get_definitions()])
        
        system_prompt = f"""
        You are a Supply Chain Execution Planner. Based on the user's intent and entities, create a step-by-step plan to answer their question.
        
        Available Tools:
        {tools_desc}
        
        Rules:
        1. Select the most appropriate tools.
        2. Map extracted entities to tool parameters.
        3. Decide if RAG (document lookup) is needed if the question is about policies or SOPs.
        4. If the intent is 'general_chat' and no tools apply, set 'fallback_to_general' to true.
        
        Output MUST be a valid JSON object:
        {{
            "steps": [
                {{
                    "tool_name": "name",
                    "arguments": {{}},
                    "rationale": "why this tool"
                }}
            ],
            "requires_rag": boolean,
            "rag_query": "query for vector search if needed",
            "fallback_to_general": boolean
        }}
        """

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Intent: {understanding.primary_intent}, Entities: {understanding.entities}, Query: {understanding.normalized_query}")
            ]
            response = await self.llm.ainvoke(messages)
            content = response.content
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            parsed = json.loads(content)
            return QueryPlan(**parsed)
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            return self._plan_fallback(understanding)

    def _plan_fallback(self, understanding: QueryUnderstandingResult) -> QueryPlan:
        steps = []
        intent = understanding.primary_intent
        
        # Simple rule-based planning for fallback/mock
        if intent == Intent.INVENTORY_STATUS:
            steps.append(ToolCall(tool_name="get_inventory_status", arguments={}))
            steps.append(ToolCall(tool_name="get_material_list", arguments={}))
            steps.append(ToolCall(tool_name="get_product_list", arguments={}))
        elif intent == Intent.INVENTORY_RISK:
            steps.append(ToolCall(tool_name="get_inventory_risk", arguments={}))
        elif intent == Intent.PO_DELAY:
            steps.append(ToolCall(tool_name="get_po_delays", arguments={}))
        elif intent == Intent.SHIPMENT_STATUS:
            steps.append(ToolCall(tool_name="get_shipment_status", arguments={}))
        elif intent == Intent.PERFORMANCE:
            steps.append(ToolCall(tool_name="get_performance_metrics", arguments={}))
        elif intent == Intent.HEALTH:
            steps.append(ToolCall(tool_name="get_health_signals", arguments={}))
        elif intent == Intent.SCENARIO_COMPARE:
            steps.append(ToolCall(tool_name="get_recommendations", arguments={}))
        elif intent == Intent.RAG_LOOKUP:
            return QueryPlan(requires_rag=True, rag_query=understanding.normalized_query)
            
        return QueryPlan(
            steps=steps,
            fallback_to_general=len(steps) == 0 and intent == Intent.GENERAL_CHAT
        )

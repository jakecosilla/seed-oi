import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from application.services.agent import SeedOIAgent, AgentState
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration

class DummyChatModel:
    async def ainvoke(self, messages):
        last_msg = messages[-1].content.lower()
        if "policy" in last_msg or "sop" in last_msg:
            intent = "rag_lookup"
        elif "delay" in last_msg:
            intent = "po_delay"
        elif "scenario" in last_msg:
            intent = "scenario_compare"
        else:
            intent = "inventory_risk"
            
        mock_json = f'{{"normalized_query": "{last_msg}", "intent": "{intent}", "entities": {{}}}}'
        return AIMessage(content=f"```json\n{mock_json}\n```")

@pytest.fixture
def mock_orchestrator():
    orchestrator = AsyncMock()
    orchestrator._handle_inventory_query.return_value = {
        "response": "Inventory is at risk for MAT-X.",
        "suggested_actions": ["Reallocate"],
        "sources": ["Inventory DB"]
    }
    orchestrator._handle_po_delay_query.return_value = {
        "response": "PO-123 is delayed.",
        "suggested_actions": ["Expedite"],
        "sources": ["PO DB"]
    }
    return orchestrator

@pytest.fixture
def agent(mock_orchestrator):
    return SeedOIAgent(db_session=AsyncMock(), chat_model=DummyChatModel(), orchestrator=mock_orchestrator)

@pytest.mark.asyncio
async def test_understand_node(agent):
    state = AgentState(
        query="what is short?",
        context={},
        tenant_id="test",
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
    new_state = await agent.understand_node(state)
    assert new_state["intent"] == "inventory_risk"
    assert new_state["normalized_query"] == "what is short?"

@pytest.mark.asyncio
async def test_route_and_execute_structured(agent, mock_orchestrator):
    state = AgentState(
        query="what is delayed?",
        context={},
        tenant_id="test",
        normalized_query="what is delayed?",
        intent="po_delay",
        entities={},
        selected_tool=None,
        structured_data=None,
        rag_context=None,
        response=None,
        suggested_actions=[],
        sources=[]
    )
    
    # Route node
    state = await agent.route_node(state)
    assert state["selected_tool"] == "structured"
    
    # Execute node
    state = await agent.execute_structured_node(state)
    assert state["structured_data"] is not None
    assert "PO-123" in state["structured_data"]["response"]
    
    # Compose node
    state = await agent.compose_node(state)
    assert state["response"] == "PO-123 is delayed."
    assert "Expedite" in state["suggested_actions"]

@pytest.mark.asyncio
async def test_rag_routing(agent):
    state = AgentState(
        query="what is the policy for allocation?",
        context={},
        tenant_id="test",
        normalized_query="policy allocation",
        intent="rag_lookup",
        entities={},
        selected_tool=None,
        structured_data=None,
        rag_context=None,
        response=None,
        suggested_actions=[],
        sources=[]
    )
    
    state = await agent.route_node(state)
    assert state["selected_tool"] == "rag"
    
    state = await agent.execute_rag_node(state)
    assert state["rag_context"] is not None
    assert "SOP-402" in state["rag_context"]
    
    state = await agent.compose_node(state)
    assert "Based on our documents:" in state["response"]
    assert "SOP-402" in state["response"]

@pytest.mark.asyncio
async def test_full_graph_invocation(agent):
    tenant_id = uuid.uuid4()
    result = await agent.run("what inventory is short?", {}, tenant_id)
    assert "Inventory is at risk" in result["response"]
    assert "Reallocate" in result["suggested_actions"]

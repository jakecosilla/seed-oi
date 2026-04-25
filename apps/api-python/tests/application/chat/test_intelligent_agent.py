import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from application.services.agent import SeedOIAgent
from application.chat.schemas import Intent, QueryUnderstandingResult, ToolCall, QueryPlan
from langchain_core.messages import AIMessage

@pytest.mark.asyncio
async def test_agent_full_flow_inventory():
    mock_db = AsyncMock()
    mock_llm = AsyncMock()
    mock_llm._llm_type = "openai" # Force non-mock path
    mock_orchestrator = MagicMock()
    
    # 1. Mock Understanding (Inventory Status)
    mock_understand_json = {
        "normalized_query": "What is the inventory status?",
        "primary_intent": "inventory_status",
        "entities": [],
        "confidence": 0.9,
        "requires_clarification": False
    }
    
    # 2. Mock Planning (Call get_inventory_status)
    mock_plan_json = {
        "steps": [
            {
                "tool_name": "get_inventory_status",
                "arguments": {},
                "rationale": "Fetch global inventory levels"
            }
        ],
        "requires_rag": False,
        "fallback_to_general": False
    }
    
    # 3. Mock Composition
    mock_composition = "Currently, there are 1,200 units on hand across all sites."

    import json
    # Mock sequence of calls to LLM
    # Node 1: Understand
    # Node 2: Plan
    # Node 3: Compose
    mock_llm.ainvoke.side_effect = [
        AIMessage(content=json.dumps(mock_understand_json)),
        AIMessage(content=json.dumps(mock_plan_json)),
        AIMessage(content=mock_composition)
    ]

    # Mock tool execution return value
    # We need to return a result that can be iterated over and has a first() method
    mock_row = (1200, 400)
    mock_result = MagicMock()
    mock_result.first.return_value = mock_row
    mock_db.execute.return_value = mock_result

    agent = SeedOIAgent(mock_db, mock_llm, mock_orchestrator)
    tenant_id = uuid.uuid4()
    
    result = await agent.run("how many items do we have?", {}, tenant_id)
    
    assert "1,200" in result["response"]
    assert "get_inventory_status" in result["sources"]
    assert len(result["suggested_actions"]) > 0

@pytest.mark.asyncio
async def test_agent_clarification_flow():
    mock_db = AsyncMock()
    mock_llm = AsyncMock()
    mock_llm._llm_type = "openai"
    
    # Mock Understanding (Ambiguous)
    mock_understand_json = {
        "normalized_query": "ambiguous",
        "primary_intent": "general_chat",
        "entities": [],
        "confidence": 0.3,
        "requires_clarification": True,
        "clarification_question": "Are you asking about materials or purchase orders?"
    }
    
    import json
    mock_llm.ainvoke.return_value = AIMessage(content=json.dumps(mock_understand_json))

    agent = SeedOIAgent(mock_db, mock_llm, None)
    result = await agent.run("tell me about the things", {}, uuid.uuid4())
    
    assert "Are you asking about materials or purchase orders?" in result["response"]
    assert result["sources"] == ["Seed OI Intelligence"]

@pytest.mark.asyncio
async def test_agent_hybrid_rag_flow():
    mock_db = AsyncMock()
    mock_llm = AsyncMock()
    mock_llm._llm_type = "openai"
    
    # 1. Mock Understanding (Policy question)
    mock_understand_json = {
        "normalized_query": "What is the policy?",
        "primary_intent": "rag_lookup",
        "entities": [],
        "confidence": 0.9,
        "requires_clarification": False
    }
    
    # 2. Mock Planning (RAG only)
    mock_plan_json = {
        "steps": [],
        "requires_rag": True,
        "rag_query": "Inventory allocation policy",
        "fallback_to_general": False
    }
    
    # 3. Mock Composition
    mock_composition = "Our policy states that strategic orders come first."

    import json
    mock_llm.ainvoke.side_effect = [
        AIMessage(content=json.dumps(mock_understand_json)),
        AIMessage(content=json.dumps(mock_plan_json)),
        AIMessage(content=mock_composition)
    ]

    agent = SeedOIAgent(mock_db, mock_llm, None)
    result = await agent.run("what is the allocation policy?", {}, uuid.uuid4())
    
    assert "strategic orders" in result["response"]
    assert "rag" in result["sources"]

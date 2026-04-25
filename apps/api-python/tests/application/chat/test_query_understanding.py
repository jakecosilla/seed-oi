import pytest
from unittest.mock import AsyncMock, MagicMock
from application.chat.query_understanding import QueryUnderstandingService
from application.chat.schemas import Intent, EntityType
from langchain_core.messages import AIMessage

@pytest.mark.asyncio
async def test_fallback_classification():
    # Service without LLM should use fallback
    service = QueryUnderstandingService(llm=None)
    result = await service.understand("what is the policy for meat?")
    
    assert result.primary_intent == Intent.RAG_LOOKUP
    assert result.is_degraded is True
    assert result.confidence == 0.4

@pytest.mark.asyncio
async def test_llm_structured_extraction():
    # Mock LLM
    mock_llm = AsyncMock()
    mock_json = {
        "normalized_query": "What inventory is at risk?",
        "primary_intent": "inventory_risk",
        "entities": [
            {"entity_type": "category", "value": "Meat", "original_text": "meat"}
        ],
        "confidence": 0.9,
        "requires_clarification": False
    }
    mock_llm.ainvoke.return_value = AIMessage(content=f"```json\nimport json\n{mock_json}\n```")
    
    # Need to handle the fact that my service might just do json.loads on the content
    # I'll fix the mock to return valid JSON string
    import json
    mock_llm.ainvoke.return_value = AIMessage(content=f"```json\n{json.dumps(mock_json)}\n```")

    service = QueryUnderstandingService(llm=mock_llm)
    result = await service.understand("is meat at risk?")
    
    assert result.primary_intent == Intent.INVENTORY_RISK
    assert result.normalized_query == "What inventory is at risk?"
    assert len(result.entities) == 1
    assert result.entities[0].entity_type == EntityType.CATEGORY
    assert result.entities[0].value == "Meat"
    assert result.is_degraded is False

@pytest.mark.asyncio
async def test_llm_failure_fallback():
    mock_llm = AsyncMock()
    mock_llm.ainvoke.side_effect = Exception("LLM Down")
    
    service = QueryUnderstandingService(llm=mock_llm)
    result = await service.understand("how many materials?")
    
    # Should fallback to keyword classifier
    assert result.primary_intent == Intent.INVENTORY_STATUS
    assert result.is_degraded is True

@pytest.mark.asyncio
async def test_invalid_json_fallback():
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = AIMessage(content="Not JSON at all")
    
    service = QueryUnderstandingService(llm=mock_llm)
    result = await service.understand("what is the stock?")
    
    # Should fallback to keyword classifier
    assert result.primary_intent == Intent.INVENTORY_STATUS
    assert result.is_degraded is True

@pytest.mark.asyncio
async def test_confidence_booster():
    # Mock LLM returns general_chat with low confidence (0.5)
    mock_llm = AsyncMock()
    mock_json = {
        "normalized_query": "Generic",
        "primary_intent": "general_chat",
        "entities": [],
        "confidence": 0.5,
        "requires_clarification": False
    }
    import json
    mock_llm.ainvoke.return_value = AIMessage(content=json.dumps(mock_json))
    
    service = QueryUnderstandingService(llm=mock_llm)
    # This query should be detected as inventory_status by the booster/fallback
    result = await service.understand("how many materials?")
    
    assert result.primary_intent == Intent.INVENTORY_STATUS
    assert result.is_degraded is True

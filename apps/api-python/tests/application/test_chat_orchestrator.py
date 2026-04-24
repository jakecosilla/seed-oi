import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock

from application.services.chat_orchestrator import ChatOrchestrator

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.fixture
def orchestrator(mock_db_session):
    tenant_id = uuid.uuid4()
    return ChatOrchestrator(mock_db_session, tenant_id)

@pytest.mark.asyncio
async def test_handle_source_query(orchestrator):
    context = {"source_id": str(uuid.uuid4())}
    result = await orchestrator.handle_query("Why is my data not updating?", context)
    
    assert "telemetry" in result["response"]
    assert "Trigger Re-Sync" in result["suggested_actions"]
    assert "System Integrations Table" in result["sources"]

@pytest.mark.asyncio
async def test_handle_issue_explanation(orchestrator, mock_db_session):
    context = {"issue_id": str(uuid.uuid4())}
    
    # Mocking the issue query result
    mock_issue = MagicMock()
    mock_issue.title = "Critical Shortage"
    mock_issue.severity = "Critical"
    mock_issue.description = "We are short on widgets."
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_issue
    mock_db_session.execute.return_value = mock_result
    
    result = await orchestrator.handle_query("Tell me more about this issue", context)
    
    assert "Critical Shortage" in result["response"]
    assert "Critical" in result["response"]
    assert "We are short on widgets." in result["response"]
    assert "View Downstream Impact" in result["suggested_actions"]
    assert "Canonical Database - Issues Table" in result["sources"]

@pytest.mark.asyncio
async def test_handle_scenario_comparison(orchestrator, mock_db_session):
    context = {"issue_id": str(uuid.uuid4())}
    
    # Mocking scenarios
    mock_scenario = MagicMock()
    mock_scenario.name = "Expedite Air Freight"
    mock_scenario.net_cost_impact = 12500.0
    mock_scenario.delay_days_avoided = 5
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_scenario]
    mock_db_session.execute.return_value = mock_result
    
    result = await orchestrator.handle_query("Compare scenarios", context)
    
    assert "Expedite Air Freight" in result["response"]
    assert "12,500.00" in result["response"]
    assert "5 days" in result["response"]
    assert "Execute Best Scenario" in result["suggested_actions"]

@pytest.mark.asyncio
async def test_handle_risk_summary(orchestrator, mock_db_session):
    mock_db_session.execute.return_value.scalar.return_value = 1500000.50
    
    result = await orchestrator.handle_query("What is my total revenue risk?")
    
    assert "1,500,001" in result["response"] or "1,500,000" in result["response"] # depending on rounding
    assert "Show high-risk issues" in result["suggested_actions"]

@pytest.mark.asyncio
async def test_handle_delay_summary(orchestrator, mock_db_session):
    mock_db_session.execute.return_value.scalar.return_value = 35
    
    result = await orchestrator.handle_query("How many delay days?")
    
    assert "35" in result["response"]
    assert "Open Scenarios" in result["suggested_actions"]

@pytest.mark.asyncio
async def test_handle_default_summary(orchestrator, mock_db_session):
    mock_db_session.execute.return_value.scalar.return_value = 7
    
    result = await orchestrator.handle_query("Hello there")
    
    assert "7 open issues" in result["response"]
    assert "What is the revenue at risk?" in result["suggested_actions"]

@pytest.mark.asyncio
async def test_handle_inventory_query_shortage(orchestrator, mock_db_session):
    # Mock shortage results
    mock_inv = MagicMock()
    mock_inv.quantity_on_hand = 10
    mock_inv.quantity_allocated = 50
    
    mock_mat = MagicMock()
    mock_mat.name = "Steel Bearings"
    mock_mat.code = "ST-100"
    
    mock_result = MagicMock()
    mock_result.all.return_value = [(mock_inv, mock_mat)]
    mock_db_session.execute.return_value = mock_result
    
    result = await orchestrator.handle_query("What inventory is at risk?")
    
    assert "Steel Bearings (ST-100)" in result["response"]
    assert "Short by 40" in result["response"]
    assert "Identify blocked orders" in result["suggested_actions"]

@pytest.mark.asyncio
async def test_handle_po_delay_query(orchestrator, mock_db_session):
    from datetime import datetime, timezone, timedelta
    
    mock_po = MagicMock()
    mock_po.order_number = "PO-9921"
    mock_po.expected_delivery_date = datetime.now(timezone.utc) - timedelta(days=10)
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_po]
    mock_db_session.execute.return_value = mock_result
    
    result = await orchestrator.handle_query("Which delayed purchase orders matter most?")
    
    assert "PO-9921" in result["response"]
    assert "10 days late" in result["response"]
    assert "Purchase Orders Table" in result["sources"]

@pytest.mark.asyncio
async def test_handle_health_query(orchestrator, mock_db_session):
    mock_db_session.execute.return_value.scalar.return_value = 142
    
    result = await orchestrator.handle_query("What inventory positions are healthy?")
    
    assert "142 material positions" in result["response"]
    assert "healthy" in result["response"]
    assert "Inventory Balance Health" in result["sources"]

@pytest.mark.asyncio
async def test_handle_refresh_query(orchestrator, mock_db_session):
    from datetime import datetime, timezone
    mock_event = MagicMock()
    mock_event.timestamp = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    mock_event.message = "sync completed successfully"
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_event
    mock_db_session.execute.return_value = mock_result
    
    result = await orchestrator.handle_query("What changed since the last refresh?")
    
    assert "2025-01-01 12:00:00 UTC" in result["response"]
    assert "sync completed successfully" in result["response"]
    assert "System Event Logs" in result["sources"]

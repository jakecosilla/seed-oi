import pytest
import uuid
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from application.security.current_user import resolve_internal_user
from application.security.authorization import auth_service
from domain.models import User, Tenant

@pytest.mark.asyncio
async def test_resolve_internal_user_existing():
    db = AsyncMock()
    token_payload = {"sub": "auth0|123", "email": "test@example.com"}
    
    mock_user = User(id=uuid.uuid4(), external_id="auth0|123", email="test@example.com", role="viewer")
    
    # Mock database result
    mock_result = AsyncMock()
    mock_result.scalars.return_value.first.return_value = mock_user
    db.execute.return_value = mock_result
    
    user = await resolve_internal_user(token_payload, db)
    assert user.external_id == "auth0|123"
    assert user.role == "viewer"

@pytest.mark.asyncio
async def test_resolve_internal_user_auto_provision_admin():
    db = AsyncMock()
    # Mock settings to include this email as admin
    with patch("application.security.current_user.settings") as mock_settings:
        mock_settings.platform_admins = ["jake.osilla@seed-grow.com"]
        mock_settings.default_tenant_id = str(uuid.uuid4())
        
        token_payload = {"sub": "auth0|admin", "email": "jake.osilla@seed-grow.com", "name": "Jake"}
        
        # Mock no user found initially
        mock_user_result = AsyncMock()
        mock_user_result.scalars.return_value.first.return_value = None
        
        # Mock tenant found
        mock_tenant = Tenant(id=uuid.UUID(mock_settings.default_tenant_id), name="Default")
        mock_tenant_result = AsyncMock()
        mock_tenant_result.scalars.return_value.first.return_value = mock_tenant
        
        db.execute.side_effect = [mock_user_result, mock_user_result, mock_tenant_result]
        
        user = await resolve_internal_user(token_payload, db)
        
        assert user.email == "jake.osilla@seed-grow.com"
        assert user.role == "admin"
        db.add.assert_called_once()
        db.commit.assert_called_once()

def test_check_tenant_access_success():
    tenant_id = uuid.uuid4()
    user = User(tenant_id=tenant_id)
    # Should not raise
    auth_service.check_tenant_access(user, tenant_id)

def test_check_tenant_access_failure():
    user = User(tenant_id=uuid.uuid4())
    with pytest.raises(HTTPException) as excinfo:
        auth_service.check_tenant_access(user, uuid.uuid4())
    assert excinfo.value.status_code == 403

def test_check_role_success():
    user = User(role="admin")
    auth_service.check_role(user, ["admin", "operator"])

def test_check_role_failure():
    user = User(role="viewer")
    with pytest.raises(HTTPException) as excinfo:
        auth_service.check_role(user, ["admin"])
    assert excinfo.value.status_code == 403

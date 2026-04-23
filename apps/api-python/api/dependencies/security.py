from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from infrastructure.auth.oidc import oidc_provider
from application.security.current_user import resolve_internal_user
from application.security.authorization import auth_service
from infrastructure.database import get_db
from domain.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    # 1. Validate external OIDC token
    payload = await oidc_provider.validate_token(token)
    
    # 2. Resolve to internal user
    user = await resolve_internal_user(payload, db)
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
        
    return user

def require_role(allowed_roles: List[str]):
    async def role_dependency(user: User = Depends(get_current_user)):
        auth_service.check_role(user, allowed_roles)
        return user
    return role_dependency

# Shorthand roles
require_admin = require_role(["admin"])
require_operator = require_role(["admin", "operator"]) # PlantManager, Planner etc map to these logically
require_viewer = require_role(["admin", "operator", "viewer"])

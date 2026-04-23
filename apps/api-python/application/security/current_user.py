from typing import Dict, Any, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends, HTTPException, status

from domain.models import User, Tenant
from infrastructure.database import get_db
from infrastructure.config import get_settings
import structlog

logger = structlog.get_logger(__name__)
settings = get_settings()

async def resolve_internal_user(
    token_payload: Dict[str, Any],
    db: AsyncSession
) -> User:
    """
    Maps an external OIDC identity to an internal Seed OI User.
    Supports auto-provisioning for configured platform admins and a default tenant.
    """
    external_id = token_payload.get("sub")
    email = token_payload.get("email")
    name = token_payload.get("name", email)

    if not external_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject (sub) claim"
        )

    # 1. Look up user by external_id (oid)
    query = select(User).where(User.external_id == external_id)
    result = await db.execute(query)
    user = result.scalars().first()

    if user:
        return user

    # 2. Fallback: look up by email (if external_id is not yet mapped)
    if email:
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        user = result.scalars().first()
        if user:
            # Map the external ID for future logins
            user.external_id = external_id
            await db.commit()
            return user

    # 3. Auto-provisioning (Pilot Mode)
    logger.info("auto_provisioning_user", email=email, external_id=external_id)
    
    # Resolve target tenant (from settings or discovered)
    target_tenant_id = uuid.UUID(settings.default_tenant_id)
    tenant_query = select(Tenant).where(Tenant.id == target_tenant_id)
    tenant_result = await db.execute(tenant_query)
    tenant = tenant_result.scalars().first()
    
    # Fallback to any tenant if default doesn't exist
    if not tenant:
        logger.warn("default_tenant_not_found", default_id=settings.default_tenant_id)
        tenant_query = select(Tenant).limit(1)
        tenant_result = await db.execute(tenant_query)
        tenant = tenant_result.scalars().first()

    if not tenant:
        logger.error("no_tenants_available_for_provisioning")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System misconfiguration: No tenants available"
        )

    # Determine role based on platform admin list
    is_platform_admin = email in settings.platform_admins if email else False
    role = "admin" if is_platform_admin else "viewer"

    new_user = User(
        id=uuid.uuid4(),
        email=email,
        name=name,
        external_id=external_id,
        tenant_id=tenant.id,
        role=role,
        is_active=True
    )
    
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except Exception as e:
        await db.rollback()
        logger.error("user_provisioning_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create internal user record"
        )

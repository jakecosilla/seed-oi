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
    email = token_payload.get("email") or f"{external_id}@auth0.local"
    name = token_payload.get("name") or token_payload.get("nickname") or email

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

    try:
        # Extract metadata with better fallback logic
        email = token_payload.get("email") or token_payload.get("preferred_username") or f"{external_id}@auth0.local"
        
        # Try to find a human-readable name
        name = token_payload.get("name") or token_payload.get("nickname") or token_payload.get("preferred_username") or external_id
        
        # Auto-provision if not found
        if not user:
            # Check if this is the first user ever (make them admin)
            from sqlalchemy import func
            user_count = await db.scalar(select(func.count(User.id)))
            initial_role = "admin" if user_count == 0 else "viewer"

            user = User(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                email=email,
                name=name,
                external_id=external_id,
                role=initial_role,
                hashed_password="oidc-managed",
                is_active=True
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(f"Auto-provisioned new user: {email} with role {initial_role}")
        else:
            # Update existing user if name was just a placeholder
            if user.name == user.external_id and name != external_id:
                user.name = name
                user.email = email
                await db.commit()
                await db.refresh(user)
        return user
    except Exception as e:
        await db.rollback()
        logger.error("user_provisioning_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DB Error: {str(e)}"
        )

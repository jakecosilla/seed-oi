from typing import List, Optional, Callable
import uuid
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from domain.models import User, Plant
import structlog

logger = structlog.get_logger(__name__)

class AuthorizationService:
    @staticmethod
    def check_tenant_access(user: User, tenant_id: uuid.UUID):
        if user.tenant_id != tenant_id:
            logger.warn("unauthorized_tenant_access_attempt", user_id=str(user.id), target_tenant=str(tenant_id))
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this tenant is not permitted"
            )

    @staticmethod
    def check_role(user: User, allowed_roles: List[str]):
        if user.role not in allowed_roles:
            logger.warn("unauthorized_role_access_attempt", user_id=str(user.id), user_role=user.role, allowed_roles=allowed_roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Action requires one of these roles: {', '.join(allowed_roles)}"
            )

    @staticmethod
    async def get_accessible_plant_ids(user: User, db: AsyncSession) -> List[uuid.UUID]:
        """
        Calculates granular plant access. 
        Admins see everything in their tenant.
        Others are restricted by the user_plants table.
        """
        if user.role == 'admin':
            query = select(Plant.id).where(Plant.tenant_id == user.tenant_id)
            result = await db.execute(query)
            return result.scalars().all()
        
        # Plant-level restrictions
        from domain.models import user_plants
        query = select(user_plants.c.plant_id).where(user_plants.c.user_id == user.id)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def check_plant_access(user: User, plant_id: uuid.UUID, db: AsyncSession):
        accessible_ids = await AuthorizationService.get_accessible_plant_ids(user, db)
        if plant_id not in accessible_ids:
            logger.warn("unauthorized_plant_access_attempt", user_id=str(user.id), plant_id=str(plant_id))
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this plant is not permitted"
            )

auth_service = AuthorizationService()

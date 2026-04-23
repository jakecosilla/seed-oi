from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from infrastructure.database import get_db
from api.schemas.settings import SettingResponse, SettingCreate, SettingUpdate, SettingHistoryResponse
from application.services.settings_service import (
    get_settings_by_category,
    create_setting,
    update_setting,
    publish_setting,
    get_setting_history
)
from application.services.observability import ObservabilityService
from api.dependencies.security import get_current_user, require_role
from application.security.authorization import auth_service
from domain.models import User

router = APIRouter(
    prefix="/settings", 
    tags=["settings"],
    dependencies=[Depends(require_role(["admin"]))]
)

@router.get("/{tenant_id}", response_model=List[SettingResponse])
async def list_settings(
    tenant_id: UUID,
    category: str = Query(..., description="Settings category (e.g., risk_rules, plant, organization)"),
    plant_id: Optional[UUID] = Query(None, description="Optional plant scope override"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List settings for a specific category, scoped to a tenant and optionally a plant.
    """
    auth_service.check_tenant_access(current_user, tenant_id)
    return await get_settings_by_category(db, tenant_id, category, plant_id)

@router.post("/{tenant_id}", response_model=SettingResponse)
async def create_new_setting(
    tenant_id: UUID,
    setting_in: SettingCreate,
    user_id: Optional[UUID] = Query(None, description="User ID making the change"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new setting draft.
    """
    auth_service.check_tenant_access(current_user, tenant_id)
    try:
        setting = await create_setting(db, tenant_id, setting_in, user_id)
        obs = ObservabilityService(db)
        await obs.log_audit(
            action="create_setting",
            entity_type="setting",
            entity_id=setting.id,
            actor_id=user_id,
            payload=setting_in.model_dump()
        )
        return setting
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{tenant_id}/{setting_id}", response_model=SettingResponse)
async def update_existing_setting(
    tenant_id: UUID,
    setting_id: UUID,
    setting_in: SettingUpdate,
    user_id: Optional[UUID] = Query(None, description="User ID making the change"),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a setting payload and record history. If it was published, it reverts to draft.
    """
    setting = await update_setting(db, tenant_id, setting_id, setting_in, user_id)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    obs = ObservabilityService(db)
    await obs.log_audit(
        action="update_setting",
        entity_type="setting",
        entity_id=setting_id,
        actor_id=user_id,
        payload=setting_in.model_dump()
    )
    return setting

@router.post("/{tenant_id}/{setting_id}/publish", response_model=SettingResponse)
async def publish_existing_setting(
    tenant_id: UUID,
    setting_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a draft setting as published.
    """
    setting = await publish_setting(db, tenant_id, setting_id)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    obs = ObservabilityService(db)
    await obs.log_audit(
        action="publish_setting",
        entity_type="setting",
        entity_id=setting_id,
        payload={"status": "published"}
    )
    return setting

@router.get("/{tenant_id}/{setting_id}/history", response_model=List[SettingHistoryResponse])
async def list_setting_history(
    tenant_id: UUID,
    setting_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve the version history of a setting.
    """
    history = await get_setting_history(db, tenant_id, setting_id)
    return history

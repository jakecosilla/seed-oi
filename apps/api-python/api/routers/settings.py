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

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("/{tenant_id}", response_model=List[SettingResponse])
async def list_settings(
    tenant_id: UUID,
    category: str = Query(..., description="Settings category (e.g., risk_rules, plant, organization)"),
    plant_id: Optional[UUID] = Query(None, description="Optional plant scope override"),
    db: AsyncSession = Depends(get_db)
):
    """
    List settings for a specific category, scoped to a tenant and optionally a plant.
    """
    return await get_settings_by_category(db, tenant_id, category, plant_id)

@router.post("/{tenant_id}", response_model=SettingResponse)
async def create_new_setting(
    tenant_id: UUID,
    setting_in: SettingCreate,
    user_id: Optional[UUID] = Query(None, description="User ID making the change"),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new setting draft.
    """
    try:
        setting = await create_setting(db, tenant_id, setting_in, user_id)
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

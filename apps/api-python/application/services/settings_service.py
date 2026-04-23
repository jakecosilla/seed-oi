from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, and_
from uuid import UUID
from typing import List, Optional, Dict, Any

from domain.models import Setting, SettingHistory
from api.schemas.settings import SettingCreate, SettingUpdate

async def get_settings_by_category(db: AsyncSession, tenant_id: UUID, category: str, plant_id: Optional[UUID] = None) -> List[Setting]:
    query = select(Setting).where(Setting.tenant_id == tenant_id, Setting.category == category)
    if plant_id:
        query = query.where(Setting.plant_id == plant_id)
    else:
        query = query.where(Setting.plant_id == None)
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_setting_by_id(db: AsyncSession, tenant_id: UUID, setting_id: UUID) -> Optional[Setting]:
    query = select(Setting).where(Setting.id == setting_id, Setting.tenant_id == tenant_id)
    result = await db.execute(query)
    return result.scalars().first()

async def create_setting(db: AsyncSession, tenant_id: UUID, setting_in: SettingCreate, user_id: Optional[UUID] = None) -> Setting:
    # Check if a setting for this category/scope already exists
    query = select(Setting).where(
        Setting.tenant_id == tenant_id,
        Setting.category == setting_in.category,
        Setting.plant_id == setting_in.plant_id,
        Setting.status == "draft"
    )
    result = await db.execute(query)
    existing = result.scalars().first()
    
    if existing:
        raise ValueError(f"Draft setting for category {setting_in.category} already exists in this scope.")

    db_setting = Setting(
        tenant_id=tenant_id,
        plant_id=setting_in.plant_id,
        category=setting_in.category,
        payload=setting_in.payload,
        status="draft"
    )
    db.add(db_setting)
    await db.flush() # flush to get the ID

    # Create history entry
    history = SettingHistory(
        setting_id=db_setting.id,
        payload=setting_in.payload,
        changed_by_user_id=user_id
    )
    db.add(history)
    
    await db.commit()
    await db.refresh(db_setting)
    return db_setting

async def update_setting(db: AsyncSession, tenant_id: UUID, setting_id: UUID, setting_in: SettingUpdate, user_id: Optional[UUID] = None) -> Optional[Setting]:
    db_setting = await get_setting_by_id(db, tenant_id, setting_id)
    if not db_setting:
        return None

    # Update payload
    db_setting.payload = setting_in.payload
    # If we update a published setting, maybe it drops back to draft? 
    # For now, we just update the payload and leave status as is, or we could force it to draft.
    # The requirement says "Support draft and published states if practical." 
    # Usually editing a published setting creates a new draft or reverts it to draft.
    db_setting.status = "draft"
    
    # Save history
    history = SettingHistory(
        setting_id=db_setting.id,
        payload=setting_in.payload,
        changed_by_user_id=user_id
    )
    db.add(history)
    
    await db.commit()
    await db.refresh(db_setting)
    return db_setting

async def publish_setting(db: AsyncSession, tenant_id: UUID, setting_id: UUID, user_id: Optional[UUID] = None) -> Optional[Setting]:
    db_setting = await get_setting_by_id(db, tenant_id, setting_id)
    if not db_setting:
        return None
        
    db_setting.status = "published"
    
    # Optional: Archive/delete older published settings in the same scope
    
    await db.commit()
    await db.refresh(db_setting)
    return db_setting

async def get_setting_history(db: AsyncSession, tenant_id: UUID, setting_id: UUID) -> List[SettingHistory]:
    # Verify ownership
    db_setting = await get_setting_by_id(db, tenant_id, setting_id)
    if not db_setting:
        return []
        
    query = select(SettingHistory).where(SettingHistory.setting_id == setting_id).order_by(SettingHistory.changed_at.desc())
    result = await db.execute(query)
    return result.scalars().all()

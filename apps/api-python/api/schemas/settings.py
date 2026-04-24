from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID

class SettingBase(BaseModel):
    category: str = Field(..., description="E.g., organization, plant, risk_rules, alert_rules, ai_assistant")
    payload: Dict[str, Any]

class SettingCreate(SettingBase):
    plant_id: Optional[UUID] = None

class SettingUpdate(BaseModel):
    payload: Dict[str, Any]

class SettingResponse(SettingBase):
    id: UUID
    tenant_id: UUID
    plant_id: Optional[UUID]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SettingHistoryResponse(BaseModel):
    id: UUID
    setting_id: UUID
    payload: Dict[str, Any]
    changed_by_user_id: Optional[UUID]
    changed_at: datetime

    class Config:
        from_attributes = True

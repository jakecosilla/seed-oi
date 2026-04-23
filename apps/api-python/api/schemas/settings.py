from pydantic import BaseModel, UUID4, Field
from typing import Dict, Any, Optional, List
from datetime import datetime

class SettingBase(BaseModel):
    category: str = Field(..., description="E.g., organization, plant, risk_rules, alert_rules, ai_assistant")
    payload: Dict[str, Any]

class SettingCreate(SettingBase):
    plant_id: Optional[UUID4] = None

class SettingUpdate(BaseModel):
    payload: Dict[str, Any]

class SettingResponse(SettingBase):
    id: UUID4
    tenant_id: UUID4
    plant_id: Optional[UUID4]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SettingHistoryResponse(BaseModel):
    id: UUID4
    setting_id: UUID4
    payload: Dict[str, Any]
    changed_by_user_id: Optional[UUID4]
    changed_at: datetime

    class Config:
        from_attributes = True

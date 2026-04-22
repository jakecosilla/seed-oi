from fastapi import APIRouter, Depends
from pydantic import BaseModel
from infrastructure.config import Settings, get_settings

router = APIRouter(prefix="/system", tags=["system"])

class VersionResponse(BaseModel):
    name: str
    version: str
    environment: str

@router.get("/version", response_model=VersionResponse)
async def get_version(settings: Settings = Depends(get_settings)) -> VersionResponse:
    """
    Get system version and environment information.
    """
    return VersionResponse(
        name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment
    )

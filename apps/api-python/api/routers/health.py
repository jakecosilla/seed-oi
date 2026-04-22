from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["system"])

class HealthResponse(BaseModel):
    status: str

@router.get("", response_model=HealthResponse)
async def check_health() -> HealthResponse:
    """
    Check the health status of the application.
    """
    return HealthResponse(status="ok")

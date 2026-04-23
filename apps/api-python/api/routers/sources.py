from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import uuid

from infrastructure.database import get_db
from api.dependencies.security import get_current_user
from domain.models import User

router = APIRouter(prefix="/sources", tags=["sources"])

# Models
class SourceConnectionStatus(BaseModel):
    id: str
    name: str
    system_type: str
    status: str
    last_synced_at: Optional[datetime]
    data_freshness_score: float
    mapping_completeness_score: float
    active_errors: int

class SyncHistoryEntry(BaseModel):
    id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    records_processed: int
    error_message: Optional[str]

class ValidationErrorDetail(BaseModel):
    id: str
    validation_type: str
    message: str
    severity: str
    created_at: datetime

# Fake Data
mock_sources = [
    SourceConnectionStatus(
        id="src-1",
        name="Global SAP ERP",
        system_type="SAP",
        status="active",
        last_synced_at=datetime.now(timezone.utc) - timedelta(minutes=15),
        data_freshness_score=0.98,
        mapping_completeness_score=0.95,
        active_errors=2
    ),
    SourceConnectionStatus(
        id="src-2",
        name="Detroit Plex MES",
        system_type="Plex",
        status="warning",
        last_synced_at=datetime.now(timezone.utc) - timedelta(hours=4),
        data_freshness_score=0.85,
        mapping_completeness_score=0.80,
        active_errors=12
    )
]

mock_sync_history = [
    SyncHistoryEntry(
        id="sync-1",
        status="success",
        started_at=datetime.now(timezone.utc) - timedelta(hours=1),
        completed_at=datetime.now(timezone.utc) - timedelta(minutes=55),
        records_processed=15000,
        error_message=None
    ),
    SyncHistoryEntry(
        id="sync-2",
        status="failed",
        started_at=datetime.now(timezone.utc) - timedelta(hours=4),
        completed_at=datetime.now(timezone.utc) - timedelta(hours=3, minutes=58),
        records_processed=450,
        error_message="Connection timeout to source API."
    )
]

mock_validation_errors = [
    ValidationErrorDetail(
        id="err-1",
        validation_type="mapping_error",
        message="Missing mapping for source field 'U_VendorID'.",
        severity="error",
        created_at=datetime.now(timezone.utc) - timedelta(hours=2)
    ),
    ValidationErrorDetail(
        id="err-2",
        validation_type="schema_error",
        message="Expected date format YYYY-MM-DD but received 'N/A'.",
        severity="warning",
        created_at=datetime.now(timezone.utc) - timedelta(hours=3)
    )
]

# Endpoints
@router.get("", response_model=List[SourceConnectionStatus])
async def list_sources(
    tenant_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all source connections with their health and completeness metrics."""
    if tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized for this tenant")
    return mock_sources

@router.get("/{source_id}/history", response_model=List[SyncHistoryEntry])
async def get_sync_history(
    source_id: str,
    tenant_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recent sync runs for a source."""
    if tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized for this tenant")
    return mock_sync_history

@router.get("/{source_id}/errors", response_model=List[ValidationErrorDetail])
async def get_source_errors(
    source_id: str,
    tenant_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """View active validation errors for a source."""
    if tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized for this tenant")
    return mock_validation_errors

@router.post("/{source_id}/retry-sync")
async def retry_sync(source_id: str):
    """Action: Trigger a manual retry for a source sync."""
    return {"status": "accepted", "message": f"Sync retry queued for source {source_id}"}

@router.post("/{source_id}/reprocess-file/{file_id}")
async def reprocess_file(source_id: str, file_id: str):
    """Action: Reprocess a previously uploaded file through the mapping layer."""
    return {"status": "accepted", "message": f"File {file_id} queued for reprocessing."}

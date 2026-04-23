from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from application.services.ingestion_service import process_csv_upload, process_excel_upload
from infrastructure.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/ingestion", tags=["ingestion"])

class ValidationFailure(BaseModel):
    row_index: int
    message: str

class IngestionSummary(BaseModel):
    filename: str
    total_rows: int
    accepted_rows: int
    failed_rows: int
    validation_messages: List[ValidationFailure]
    file_metadata: Dict[str, Any]

@router.post("/upload", response_model=IngestionSummary)
async def upload_file(
    file: UploadFile = File(...),
    tenant_id: str = Form(...),
    source_connection_id: str = Form(...),
    entity_type: str = Form(...),
    db: AsyncSession = Depends(get_db)
) -> IngestionSummary:
    """
    Upload a CSV or Excel file to parse into staging raw_source_payloads.
    """
    if not file.filename.endswith(('.csv', '.xlsx')):
        raise HTTPException(status_code=400, detail="Only CSV and XLSX files are supported.")

    content = await file.read()
    
    if file.filename.endswith('.csv'):
        result = await process_csv_upload(content, file.filename, tenant_id, source_connection_id, entity_type, db)
    else:
        result = await process_excel_upload(content, file.filename, tenant_id, source_connection_id, entity_type, db)

    if result.failed_rows > 0:
        from application.services.observability import ObservabilityService
        obs = ObservabilityService(db)
        await obs.emit_system_event(
            event_type="ingestion_failure",
            message=f"Ingestion for {file.filename} had {result.failed_rows} failures.",
            severity="warning",
            metadata={
                "filename": result.filename,
                "total_rows": result.total_rows,
                "failed_rows": result.failed_rows,
                "validation_messages": [m.dict() for m in result.validation_messages]
            }
        )

    return IngestionSummary(
        filename=result.filename,
        total_rows=result.total_rows,
        accepted_rows=result.accepted_rows,
        failed_rows=result.failed_rows,
        validation_messages=result.validation_messages,
        file_metadata=result.file_metadata
    )

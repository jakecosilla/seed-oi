from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from application.services.ingestion_service import process_csv_upload, process_excel_upload

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
    entity_type: str = Form(...)
) -> IngestionSummary:
    """
    Upload a CSV or Excel file to parse into staging raw_source_payloads.
    """
    if not file.filename.endswith(('.csv', '.xlsx')):
        raise HTTPException(status_code=400, detail="Only CSV and XLSX files are supported.")

    content = await file.read()
    
    if file.filename.endswith('.csv'):
        result = await process_csv_upload(content, file.filename, tenant_id, source_connection_id, entity_type)
    else:
        result = await process_excel_upload(content, file.filename, tenant_id, source_connection_id, entity_type)

    return IngestionSummary(
        filename=result.filename,
        total_rows=result.total_rows,
        accepted_rows=result.accepted_rows,
        failed_rows=result.failed_rows,
        validation_messages=result.validation_messages,
        file_metadata=result.file_metadata
    )

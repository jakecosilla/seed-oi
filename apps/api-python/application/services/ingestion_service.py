import csv
import io
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class IngestionResult:
    def __init__(self, filename: str):
        self.filename = filename
        self.total_rows = 0
        self.accepted_rows = 0
        self.failed_rows = 0
        self.validation_messages = []
        self.file_metadata = {}

async def process_csv_upload(content: bytes, filename: str, tenant_id: str, source_id: str, entity_type: str) -> IngestionResult:
    result = IngestionResult(filename=filename)
    result.file_metadata = {
        "size_bytes": len(content),
        "tenant_id": tenant_id,
        "source_connection_id": source_id,
        "entity_type": entity_type,
        "format": "csv"
    }
    
    try:
        text = content.decode('utf-8-sig') # Handle BOM if present
        reader = csv.DictReader(io.StringIO(text))
        
        for idx, row in enumerate(reader, start=1):
            result.total_rows += 1
            
            # Basic validation: check if row is completely empty
            if not any(val.strip() for val in row.values() if val):
                result.failed_rows += 1
                result.validation_messages.append({"row_index": idx, "message": "Row is completely empty."})
                continue
                
            # TODO: Integrate SQLAlchemy Repository to save row to `raw_source_payloads` table
            # Example: db.add(RawSourcePayload(tenant_id=tenant_id, raw_payload=row, status="pending"))
            
            result.accepted_rows += 1
    except Exception as e:
        logger.error(f"Failed to parse CSV file {filename}: {e}")
        result.validation_messages.append({"row_index": 0, "message": f"File parsing error: {str(e)}"})
        
    logger.info(f"Processed CSV {filename}: {result.accepted_rows} accepted, {result.failed_rows} failed.")
    return result

async def process_excel_upload(content: bytes, filename: str, tenant_id: str, source_id: str, entity_type: str) -> IngestionResult:
    import openpyxl
    result = IngestionResult(filename=filename)
    result.file_metadata = {
        "size_bytes": len(content),
        "tenant_id": tenant_id,
        "source_connection_id": source_id,
        "entity_type": entity_type,
        "format": "xlsx"
    }
    
    try:
        wb = openpyxl.load_workbook(filename=io.BytesIO(content), read_only=True, data_only=True)
        ws = wb.active
        
        headers = []
        for idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
            if idx == 1:
                headers = [str(cell) if cell is not None else f"col_{i}" for i, cell in enumerate(row)]
                continue
                
            result.total_rows += 1
            if not any(row):
                result.failed_rows += 1
                result.validation_messages.append({"row_index": idx, "message": "Row is completely empty."})
                continue
            
            # Map row to dictionary
            row_dict = dict(zip(headers, row))
            
            # TODO: Integrate SQLAlchemy Repository to save to `raw_source_payloads` table
            
            result.accepted_rows += 1
    except Exception as e:
        logger.error(f"Failed to parse Excel file {filename}: {e}")
        result.validation_messages.append({"row_index": 0, "message": f"File parsing error: {str(e)}"})
        
    logger.info(f"Processed Excel {filename}: {result.accepted_rows} accepted, {result.failed_rows} failed.")
    return result

# Seed OI Ingestion Lifecycle

To maintain trust and isolate messy external data from the clean business logic, Seed OI employs a robust **Staging and Mapping Layer**. 

External data is *never* ingested directly into the canonical business tables.

## The 4-Step Ingestion Lifecycle

### 1. Ingestion (Status: `pending`)
- Data is received from a source system (e.g., SAP via API) or a manual file upload (e.g., CSV).
- The raw JSON or parsed CSV row is inserted into the `raw_source_payloads` table.
- At this stage, the data is completely untyped and unvalidated, stored exactly as received.
- Its status is set to `pending`.

### 2. Validation (Status: `validated` or `failed`)
- Background workers pick up `pending` payloads.
- The raw payload is checked against expected base structures for the integration.
- If the payload is fundamentally corrupt, missing critical identifiers, or unreadable, the status changes to `failed` and an error is written to the `validation_logs` table.
- If the basic structure is intact, the status changes to `validated`.

### 3. Mapping 
- The system reads `mapping_rules` defined for the specific `tenant_id` and `source_connection_id`.
- The rules dictate how a `source_field` (e.g., `U_MaterialCode`) maps to a `canonical_field` (e.g., `materials.code`).
- `transformation_logic` is applied if necessary (e.g., ISO date parsing, string trimming).
- If mapping fails due to a missing mapping rule or invalid type conversion, the status is set to `failed` and a `validation_log` is created.

### 4. Canonical Upsert (Status: `mapped`)
- If mapping succeeds, a canonical entity (e.g., a `Material` or `WorkOrder` model) is constructed.
- The entity is upserted (Insert or Update) into the respective canonical table.
- The `raw_source_payload` status is updated to `mapped`.
- The canonical entity's `last_synced_at` timestamp is updated to reflect freshness.

## Benefits
- **Replayability:** If a mapping rule is incorrect or incomplete, we can update the rule and re-process all `mapped` or `failed` payloads directly from the database without needing to hit the ERP APIs again.
- **Auditability:** We can trace any canonical record back to the exact JSON payload that generated it.
- **Isolation:** Non-standard or messy ERP schemas do not pollute the Seed OI canonical model.

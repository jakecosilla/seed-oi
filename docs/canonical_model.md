# Seed OI Canonical Operational Model

The Seed OI canonical model is designed to be completely ERP-agnostic. By translating disparate data from SAP, NetSuite, Plex, or spreadsheets into these universal supply chain concepts, the application layer remains clean and logic-driven.

## Core Traceability

Every operational entity includes universal traceability fields to maintain trust and auditability:
- `tenant_id`: Multi-tenant data isolation.
- `plant_id`: Associates records with a specific site/facility.
- `source_system`: Identifies the system of record (e.g., SAP, Plex, CSV_Upload).
- `source_record_id`: The exact ID of the record in the original system.
- `last_synced_at`: Timestamp indicating data freshness.

## Entities and Relationships

### 1. Master Data
- **Products**: Finished goods ready for shipment.
- **Materials**: Raw materials and components required for production.
- **Vendors**: Suppliers of raw materials.
- **Customers**: Buyers of finished products.

### 2. Supply & Demand
- **Inventory Balances**: Current stock levels for materials and products at specific locations. *(Relates to Materials or Products)*
- **Purchase Orders**: Supply-side orders placed with vendors. *(Relates to Vendors)*
- **Sales Orders**: Demand-side orders placed by customers. *(Relates to Customers)*

### 3. Execution
- **Work Orders**: Planned production jobs to convert materials into products. *(Relates to Products)*
- **Production Runs**: The actual execution phase of a work order on the factory floor. *(Relates to Work Orders)*
- **Shipments**: Logistical fulfillment of sales orders to customers. *(Relates to Sales Orders)*

### 4. Intelligence & Decisions
- **Issues**: Root cause problems detected in the supply chain (e.g., Supplier Delay, Material Shortage).
- **Risks**: Downstream impact vectors linked to an issue (e.g., Work Order Delay resulting from a Material Shortage). *(Relates to Issues)*
- **Scenarios**: Potential resolution paths to mitigate an issue. *(Relates to Issues)*
- **Recommendations**: Specific actionable steps (Expedite, Reallocate, Reschedule) evaluated within a scenario. *(Relates to Scenarios)*

## Architecture Guidelines
- External connectors map external data strictly to these canonical tables.
- Visual layers and AI services operate exclusively on this canonical model.
- Business logic evaluates supply risks by traversing the operational graph: `Purchase Orders` -> `Materials` -> `Work Orders` -> `Products` -> `Sales Orders`.

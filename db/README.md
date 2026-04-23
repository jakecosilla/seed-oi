# Seed OI Database Baseline

This directory contains the database schema definitions and Alembic migrations for the Seed OI canonical data model.

## Initial Foundational Tables
- **tenants**: Multi-tenant isolation at the root level.
- **users**: Tenant-scoped users.
- **plants**: Tenant-scoped manufacturing plants/sites.
- **source_connections**: Track external ERP/MES connections per tenant.
- **source_sync_runs**: Audit logs of sync operations for observability.

## Local Setup

1. Ensure you have PostgreSQL running locally (e.g., via Docker).
2. Create a local database named `seed_oi`:
   ```bash
   createdb seed_oi
   ```
3. Update `sqlalchemy.url` in `alembic.ini` to point to your local database if it differs from the default `postgresql://postgres:postgres@localhost:5432/seed_oi`.
4. Create a virtual environment and install dependencies:
   ```bash
   cd db
   uv venv
   source .venv/bin/activate
   uv sync
   ```
5. Run the initial migration to build the schema:
   ```bash
   alembic upgrade head
   ```

## Seeding Demo Data

For local demonstrations, you can populate the canonical schema with deterministic, realistic demo data (plants, vendors, materials, inventory, orders, issues, risks, and scenarios) without needing a live ERP integration.

1. Ensure the database schema is up-to-date (`alembic upgrade head`).
2. Run the seed script:
   ```bash
   python seed.py
   ```
   *Note: This script will truncate existing tables before inserting the deterministic storyline data, allowing you to easily reset the demo environment.*

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
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
5. Run the initial migration to build the schema:
   ```bash
   alembic upgrade head
   ```

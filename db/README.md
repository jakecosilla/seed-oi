# Seed OI Database & Data Layer

This directory contains the database schema (managed by Alembic), data models, and seeding scripts for the Seed OI platform.

## Local Setup

### 1. Start PostgreSQL
The platform requires PostgreSQL running on port `5432`. Use Docker to start a fresh instance:

```bash
docker run --name seed-oi-db -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
```

### 2. Create the Database
Create the internal `seed_oi` database:

```bash
docker exec -it seed-oi-db createdb -U postgres seed_oi
```

### 3. Initialize Schema (Migrations)
We use `uv` for lightning-fast Python dependency management. Ensure you have `uv` installed:

```bash
cd db
uv run alembic upgrade head
```

### 4. Seed Data
To populate the database with demo users, plants, and scenarios:

```bash
uv run python seed.py
```

## Schema Management

- **Add a new table/column**:
  1. Update models in `apps/api-python/domain/models.py` or `apps/worker-python/domain/models.py`.
  2. Generate a migration: `uv run alembic revision -m "description"`
  3. Edit the generated file in `alembic/versions/`.
  4. Apply: `uv run alembic upgrade head`

## Important Tables

- `tenants`: Multi-tenant isolation layer.
- `users`: Identity and RBAC (Admin, PlantManager, etc.).
- `plants`: Physical factory locations.
- `source_connections`: External system integration points.
- `issues`: AI-detected operational disruptions.
- `risks`: Impact analysis for detected issues.
- `scenarios`: Proposed mitigation strategies.

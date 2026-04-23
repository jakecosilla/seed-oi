# Seed OI

Seed OI is a visual operations intelligence platform for manufacturers. It serves as a decision layer on top of existing operational systems (ERP, MES, WMS) to help teams understand what is wrong, where it started, what it will affect next, and what action to take.

## Monorepo Structure

- `apps/web`: Next.js web application frontend.
- `apps/api-python`: Python FastAPI orchestration services.
- `apps/worker-python`: Python background workers for AI intelligence.
- `db`: Database schema (Alembic), seed data, and migrations.
- `docs`: Auth0 SSO setup, guides, and architecture docs.

## Getting Started

### 1. Prerequisites
- Node.js 18+
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- Docker Desktop (for PostgreSQL)

### 2. Database Setup
Ensure PostgreSQL is running and migrations are applied:
```bash
# Start Docker DB
docker run --name seed-oi-db -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
docker exec -it seed-oi-db createdb -U postgres seed_oi

# Run migrations and seed data using uv
cd db
uv run alembic upgrade head
uv run python seed.py
```

### 3. Authentication Setup (Auth0)
Configure your SSO provider by following the [Auth0 Setup Guide](docs/auth0_setup.md).

### 4. Run Locally
Start all services (Frontend, API, Worker) using the helper script:
```bash
./run_local.sh
```

Visit `http://localhost:3000` to access the platform.

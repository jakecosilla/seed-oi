# Seed OI

Seed OI is a visual operations intelligence platform for manufacturers. It serves as a decision layer on top of existing operational systems (ERP, MES, WMS) to help teams understand what is wrong, where it started, what it will affect next, and what action to take.

## Monorepo Structure

- `apps/web`: Next.js web application frontend.
- `apps/api-python`: Python AI and orchestration services.
- `apps/worker-python`: Python background workers.
- `packages/contracts`: Shared schemas, types, and contracts.
- `db`: Database schema definitions, seed data, and migrations.
- `docs`: Project documentation, including Architecture Decision Records (ADRs).
- `services-future/`: Placeholders for future .NET platform APIs and connectors.

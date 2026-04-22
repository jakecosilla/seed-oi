# Seed OI API Service (Python)

This directory contains the Python AI and orchestration services, built using FastAPI.

## Architecture

The project follows a clean architecture approach:
- `api/`: API controllers, routers, and request/response models.
- `application/`: Application layer services and use cases (business logic orchestration).
- `domain/`: Core business entities, models, and domain interfaces.
- `infrastructure/`: External integrations, database access, and configuration.

## Running Locally

1. Setup a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   # or
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`.
You can access the Swagger documentation at `http://localhost:8000/docs`.

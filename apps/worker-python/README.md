# Seed OI Background Worker (Python)

This directory contains the Python background worker process responsible for scheduled syncs, file ingestion, and heavy computations like risk recomputation. 

It is designed to run completely independently from the user-facing HTTP API process.

## Architecture

The project structure is designed for modular background processing:
- `jobs/`: Contains independent task logic (e.g., file ingestion, syncing, risk models).
- `infrastructure/`: External integrations, database access, and configuration.
- `main.py`: The daemon entry point that orchestrates listening to queues, message brokers, or local schedulers.

*Note: In the future, this architecture allows easy integration with production task orchestrators like Celery, Temporal, or ARQ.*

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

3. Run the worker process:
   ```bash
   python main.py
   ```

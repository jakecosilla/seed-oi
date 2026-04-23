#!/bin/bash

echo "==========================================="
echo "Starting Seed OI Local Development Services"
echo "==========================================="

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "==========================================="
    echo "Shutting down all Seed OI services..."
    echo "==========================================="
    # Kill all background jobs started by this script
    kill $(jobs -p) 2>/dev/null
    wait 2>/dev/null
    echo "All services gracefully stopped."
    exit 0
}

# Trap SIGINT (Ctrl+C) and SIGTERM to run the cleanup function
trap cleanup SIGINT SIGTERM

# 1. Start the Web Frontend
echo "[1/3] Starting Next.js Web Frontend (Port 3000)..."
(cd apps/web && npm run dev) &

# 2. Start the Python API Service
echo "[2/3] Starting Python API Service (Port 8000)..."
(
    cd apps/api-python
    # Activate virtual environment if it exists locally or in the root/db
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    elif [ -d "../../db/.venv" ]; then
        source ../../db/.venv/bin/activate
    fi
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
) &

# 3. Start the Python Worker Service
echo "[3/3] Starting Python Worker Service..."
(
    cd apps/worker-python
    # Activate virtual environment if it exists locally or in the root/db
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    elif [ -d "../../db/.venv" ]; then
        source ../../db/.venv/bin/activate
    fi
    python main.py
) &

echo "==========================================="
echo "✅ All services are booting up in the background."
echo "Press Ctrl+C at any time to stop everything."
echo "==========================================="

# Keep script running and wait for background processes
wait

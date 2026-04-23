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
    if command -v uv &> /dev/null; then
        uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    else
        [ -d ".venv" ] && source .venv/bin/activate
        uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    fi
) &

# 3. Start the Python Worker Service
echo "[3/3] Starting Python Worker Service..."
(
    cd apps/worker-python
    if command -v uv &> /dev/null; then
        uv run python main.py
    else
        [ -d ".venv" ] && source .venv/bin/activate
        python main.py
    fi
) &

echo "==========================================="
echo "✅ All services are booting up in the background."
echo "Press Ctrl+C at any time to stop everything."
echo "==========================================="

# Keep script running and wait for background processes
wait

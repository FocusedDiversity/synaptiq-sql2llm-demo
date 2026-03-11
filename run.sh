#!/usr/bin/env bash
set -euo pipefail

# Cleanup function to kill both processes on exit
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    echo "Done."
}
trap cleanup EXIT INT TERM

# Activate venv if not already active
if [ -z "${VIRTUAL_ENV:-}" ]; then
    source .venv/bin/activate
fi

echo "Starting backend on http://localhost:8000..."
uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Starting frontend on http://localhost:5173..."
cd frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "Press Ctrl+C to stop both."

wait

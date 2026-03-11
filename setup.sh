#!/usr/bin/env bash
set -euo pipefail

echo "=== Synaptiq SQL2LLM Demo Setup ==="

# Python virtual environment
echo "[1/4] Creating Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Python dependencies
echo "[2/4] Installing Python dependencies..."
pip install -e ".[dev]" --quiet

# Frontend dependencies
echo "[3/4] Installing frontend dependencies..."
cd frontend
npm install --silent
cd ..

# Seed database
echo "[4/4] Seeding database..."
python -m backend.seed

echo ""
echo "=== Setup complete! ==="
echo "1. Copy .env.example to .env and add your ANTHROPIC_API_KEY"
echo "2. Run ./run.sh to start the application"

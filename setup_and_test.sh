#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "🚀 Futuroscope Commuter - Automated Setup & Test Runner"
echo "=========================================================="

# Check Python version
python3 --version

# Verify virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install -r backend/requirements.txt -r frontend/requirements.txt
fi

# Run pytest
echo ""
echo "🧪 Running Pytest Test Suite..."
PYTHONPATH=backend ./venv/bin/pytest backend/tests -v

echo ""
echo "✅ All tests passed successfully!"
echo "To start the backend:  make run-backend   (or PYTHONPATH=backend ./venv/bin/uvicorn app.main:app --reload)"
echo "To start the frontend: make run-frontend  (or ./venv/bin/streamlit run frontend/app.py)"
echo "Or with Docker:        docker-compose up --build"

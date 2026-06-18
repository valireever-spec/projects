#!/bin/bash
set -e

# Run Business Dev Platform server
cd "$(dirname "$0")"

echo "🚀 Business Dev Platform - Starting server..."
echo ""
echo "Environment: Development"
echo "URL: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing/updating dependencies..."
pip install -q -r requirements.txt

echo "Starting FastAPI server..."
python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000

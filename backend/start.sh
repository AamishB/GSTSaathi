#!/bin/bash
# Quick start script for GSTSaathi backend development

echo "=== GSTSaathi Backend Quick Start ==="

# Check Python version
echo "Checking Python version..."
python --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
python -m pip install -r requirements.txt

# Copy .env.example to .env if .env doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "IMPORTANT: Edit .env and add your GEMINI_API_KEY"
fi

# Create necessary directories
mkdir -p uploads/invoices uploads/gstr2b exports gst_law_db

# Run database migrations (create tables)
echo "Initializing database..."
python -c "from app.database import init_db; init_db()"

# Start the server
echo ""
echo "=== Starting FastAPI server ==="
echo "API Docs: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/health"
echo ""
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

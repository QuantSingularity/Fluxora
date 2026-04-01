#!/bin/bash
# Fluxora Backend Startup Script
set -e

echo "========================================="
echo " Fluxora Backend Startup"
echo "========================================="

# Require Python 3.9+
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_major=3
required_minor=9
IFS='.' read -r major minor patch <<< "$python_version"
if [ "$major" -lt "$required_major" ] || { [ "$major" -eq "$required_major" ] && [ "$minor" -lt "$required_minor" ]; }; then
    echo "ERROR: Python $required_major.$required_minor+ required, found $python_version" >&2
    exit 1
fi
echo "✓ Python $python_version"

# Install dependencies if requested
if [ "$1" == "--install" ]; then
    echo "Installing dependencies..."
    pip install -q --no-input -r requirements.txt
    echo "✓ Dependencies installed"
fi

# Load .env if present
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✓ Loaded .env"
fi

# Initialise database
echo "Initialising database..."
python3 -c "from backend.database import init_db; init_db()"
echo "✓ Database ready"

# Optional: train model if not present
MODEL_PATH=${MODEL_PATH:-./fluxora_model.joblib}
if [ ! -f "$MODEL_PATH" ] && [ "$AUTO_TRAIN" == "true" ]; then
    echo "No model found – running training pipeline..."
    python3 -c "from models.train import run_training_pipeline; run_training_pipeline()"
    echo "✓ Model trained"
fi

# Start server
HOST=${API_HOST:-0.0.0.0}
PORT=${API_PORT:-8000}
WORKERS=${API_WORKERS:-1}

echo "Starting Fluxora API..."
echo "  URL    : http://$HOST:$PORT"
echo "  Docs   : http://$HOST:$PORT/docs"
echo "  Workers: $WORKERS"
echo "========================================="

exec python3 -m uvicorn main:app \
    --host "$HOST" \
    --port "$PORT" \
    --workers "$WORKERS"

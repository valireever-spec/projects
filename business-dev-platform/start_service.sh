#!/bin/bash
# Business Dev Platform Service Startup Script
# Finds an available port starting from 8000 and starts the service

# Set PATH explicitly for systemd environment
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

PROJECT_DIR="/home/vali/projects/business-dev-platform"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/app.log"

# Create log directory in project (easier permissions)
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR" 2>/dev/null || true
fi

# Activate virtual environment
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate" 2>/dev/null || true
fi

# Function to check if port is available
is_port_available() {
    (echo >/dev/tcp/127.0.0.1/$1) 2>/dev/null
    return $?
}

# Find available port starting from 8000
PORT=8000
MAX_PORT=8010

while [ $PORT -le $MAX_PORT ]; do
    if ! is_port_available $PORT 2>/dev/null; then
        echo "$(date): Port $PORT is available. Starting service on http://localhost:$PORT" >> "$LOG_FILE" 2>&1
        break
    else
        echo "$(date): Port $PORT is in use, trying next..." >> "$LOG_FILE" 2>&1
        PORT=$((PORT + 1))
    fi
done

if [ $PORT -gt $MAX_PORT ]; then
    echo "$(date): Error: No available ports found between 8000-$MAX_PORT" >> "$LOG_FILE" 2>&1
    exit 1
fi

# Write port to a file for reference
echo $PORT > "$PROJECT_DIR/.service_port" 2>/dev/null || true

# Log startup info
echo "$(date): Starting Business Dev Platform on port $PORT" >> "$LOG_FILE" 2>&1

# Start the application
cd "$PROJECT_DIR"
exec python3 -m uvicorn backend.api.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --log-level info >> "$LOG_FILE" 2>&1

#!/bin/bash

# =========================
# DAILY PIPELINE CRON WRAPPER
# =========================
# This script ensures proper environment setup for cron execution

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$BACKEND_DIR")"

# Change to backend directory
cd "$BACKEND_DIR" || exit 1

# Load environment variables from .env file
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
fi

# Log file location
LOG_DIR="$BACKEND_DIR/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/daily_pipeline_$(date +%Y%m%d_%H%M%S).log"

# Log start
echo "==========================" >> "$LOG_FILE"
echo "Pipeline started at: $(date)" >> "$LOG_FILE"
echo "Working directory: $(pwd)" >> "$LOG_FILE"
echo "Python: $(which python3)" >> "$LOG_FILE"
echo "MONGO_URI: ${MONGO_URI:0:20}..." >> "$LOG_FILE"
echo "==========================" >> "$LOG_FILE"

# Run the pipeline
python3 "$SCRIPT_DIR/daily_pipeline.py" >> "$LOG_FILE" 2>&1

# Log completion
EXIT_CODE=$?
echo "==========================" >> "$LOG_FILE"
echo "Pipeline finished at: $(date)" >> "$LOG_FILE"
echo "Exit code: $EXIT_CODE" >> "$LOG_FILE"
echo "==========================" >> "$LOG_FILE"

# Keep only last 30 days of logs
find "$LOG_DIR" -name "daily_pipeline_*.log" -mtime +30 -delete

exit $EXIT_CODE

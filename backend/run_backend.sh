#!/bin/bash

# 1. Start PostgreSQL (Skipped in Docker / Manual for Local)
# echo "Starting PostgreSQL..."
# sudo service postgresql start || echo "Warning: PostgreSQL start failed"

# 2. Run Backend using absolute path to python in museed_backend env
# This avoids 'conda activate' issues in non-interactive shells
echo "Starting MUSEED Backend Server..."
# Add current directory AND sibling MuQ directory to PYTHONPATH for easy local execution
export PYTHONPATH=$PYTHONPATH:$(pwd):$(pwd)/../../MuQ
# Run Server (Docker friendly)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

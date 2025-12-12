#!/bin/bash

# 1. Start PostgreSQL (User verification might be needed for sudo)
echo "Starting PostgreSQL..."
sudo service postgresql start || echo "Warning: PostgreSQL start failed (might be running or permission denied)"

# 2. Run Backend using absolute path to python in museed_backend env
# This avoids 'conda activate' issues in non-interactive shells
echo "Starting MUSEED Backend Server..."
export PYTHONPATH=$PYTHONPATH:$(pwd)
/home/jay/EMAs/gate/mambaforge/envs/museed_backend/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

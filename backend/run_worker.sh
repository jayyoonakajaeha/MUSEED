#!/bin/bash

# Activate Conda Env if needed (Optional, assumes user does it)
# source ~/EMAs/gate/mambaforge/etc/profile.d/conda.sh
# conda activate museed_backend

echo "Starting Celery Worker (Local)..."
export PYTHONPATH=$PYTHONPATH:$(pwd):$(pwd)/../../MuQ
export IS_CELERY_WORKER=true

# Run Celery Worker
# -A: App instance
# -P solo: Fixes CUDA fork issues on Windows/Linux with GPU
# -l info: Log level
celery -A app.worker.celery_app worker --loglevel=info -P solo

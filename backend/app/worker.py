
from celery import Celery
import os

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "museed",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.tasks"]
)

# Model loading and quantization logic, executed when the worker starts

# Model loading is handled in app.tasks when imported


celery_app.conf.update(
    task_routes={
        "app.tasks.generate_playlist_task": "celery",
        "app.tasks.generate_playlist_from_id_task": "celery",
    },
    worker_concurrency=1,  # 중요: GPU OOM 방지용 단일 스레드
    worker_prefetch_multiplier=1, # 프리패치 없음
    task_track_started=True,
    task_time_limit=300, # 5 minutes max
)

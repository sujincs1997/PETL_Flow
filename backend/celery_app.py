# backend/celery_app.py
import os
from celery import Celery
from .config import settings

# Use Redis (or fallback to localhost) for broker and backend
def get_redis_url():
    return getattr(settings, "REDIS_URL", "redis://localhost:6379/0")

redis_url = get_redis_url()

celery_app = Celery(
    "etl_flow",
    broker=redis_url,
    backend=redis_url,
    include=["backend.engine.tasks"],
)

# Basic configuration – adjust as needed for production
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

if __name__ == "__main__":
    celery_app.start()

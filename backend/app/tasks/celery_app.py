"""Celery application configuration."""

from celery import Celery
import os

celery_app = Celery(
    "sponsor_platform",
    broker=os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1"),
)

celery_app.conf.update(
    # Task settings
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,

    # Queue routing
    task_routes={
        "app.tasks.agent_tasks.*": {"queue": "agent"},
        "app.tasks.email_tasks.*": {"queue": "email"},
    },

    # Default queue
    task_default_queue="default",

    # Retry settings
    task_acks_late=True,
    worker_prefetch_multiplier=1,

    # Beat schedule (Phase 07 & 10)
    beat_schedule={
        "send-followup-batch": {
            "task": "app.tasks.email_tasks.send_followup_batch",
            "schedule": 3600.0,  # Every hour
        },
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])

from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "finpulse",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Scheduled tasks
celery_app.conf.beat_schedule = {
    "sync-accounting-data": {
        "task": "app.tasks.sync_tasks.sync_all_accounting",
        "schedule": crontab(minute=0, hour="*/6"),  # Every 6 hours
    },
    "sync-marketing-data": {
        "task": "app.tasks.sync_tasks.sync_all_marketing",
        "schedule": crontab(minute=0, hour="*"),  # Every hour
    },
    "generate-daily-insights": {
        "task": "app.tasks.insight_tasks.generate_daily_insights",
        "schedule": crontab(minute=0, hour=8),  # Daily at 8 AM UTC
    },
    "evaluate-alerts": {
        "task": "app.tasks.alert_tasks.evaluate_all_alerts",
        "schedule": crontab(minute="*/30"),
    },
    "process-abandoned-checkouts": {
        "task": "app.tasks.abandoned_cart_tasks.process_abandoned_checkouts",
        "schedule": crontab(minute="*/15"),
    },
}

celery_app.autodiscover_tasks(["app.tasks"])

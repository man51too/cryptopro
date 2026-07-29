"""
Celery configuration for background tasks.
"""
from celery import Celery
from typing import Any, Dict
import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def create_celery_app() -> Celery:
    """
    Create and configure Celery application.
    
    Returns:
        Celery: Configured Celery instance
    """
    celery_app = Celery(
        "cryptopro",
        broker=settings.CELERY_BROKER_URL,
        backend=settings.CELERY_RESULT_BACKEND,
        include=[
            "app.workers.price_updater",
            "app.workers.ai_calculator",
            "app.workers.alert_checker",
        ],
    )
    
    # Celery configuration
    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=300,
        task_soft_time_limit=240,
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=100,
        broker_connection_retry_on_startup=True,
        broker_pool_limit=10,
        result_expires=3600,
    )
    
    return celery_app


celery_app = create_celery_app()

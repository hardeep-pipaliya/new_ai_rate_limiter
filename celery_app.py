"""
Celery application configuration
"""
from app import celery

# Import tasks to register them with Celery
from app.tasks import worker_tasks

# Make sure tasks are registered
celery.autodiscover_tasks(['app.tasks']) 
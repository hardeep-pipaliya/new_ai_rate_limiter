"""
Celery configuration for AI Rate Limiter
"""
import os

# Celery Configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'amqp://guest:guest@rabbitmq:5672/')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

# Task Configuration
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes

# Beat Configuration (for scheduled tasks)
CELERY_BEAT_SCHEDULER = 'celery.beat.PersistentScheduler'
CELERY_BEAT_SCHEDULE = {
    'cleanup-expired-data': {
        'task': 'app.tasks.worker_tasks.cleanup_expired_data',
        'schedule': 3600.0,  # Run every hour
    },
} 
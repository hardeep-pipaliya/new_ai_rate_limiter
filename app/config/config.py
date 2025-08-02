"""
Configuration settings for the AI Rate Limiter application
"""
import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@postgres:5432/ai_rate_limiter')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis Configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
    
    # RabbitMQ Configuration
    RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@rabbitmq:5672/')
    
    # Celery Configuration
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'amqp://guest:guest@rabbitmq:5672/')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'UTC'
    CELERY_ENABLE_UTC = True
    CELERY_TASK_TRACK_STARTED = True
    CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
    
    # APISIX Configuration
    APISIX_GATEWAY_URL = os.getenv('APISIX_GATEWAY_URL', 'http://apisix:9080')
    APISIX_ADMIN_URL = os.getenv('APISIX_ADMIN_URL', 'http://apisix:9180')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # Batch Processing Configuration
    BATCH_TIMEOUT = timedelta(minutes=30)
    MAX_BATCH_SIZE = 1000
    
    # Rate Limiting Configuration
    DEFAULT_RATE_LIMIT = 1000
    DEFAULT_TIME_WINDOW = 3600  # 1 hour in seconds 
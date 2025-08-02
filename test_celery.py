#!/usr/bin/env python3
"""
Test script for Celery connectivity
"""
import os
import sys
import time
from celery import Celery

def test_celery_connection():
    """Test Celery broker and result backend connectivity"""
    
    # Create Celery app
    app = Celery('test')
    
    # Configure Celery
    app.conf.update(
        broker_url=os.getenv('CELERY_BROKER_URL', 'amqp://guest:guest@rabbitmq:5672/'),
        result_backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0'),
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
    )
    
    print("🧪 Testing Celery Connectivity...")
    
    # Test broker connection
    try:
        print("📡 Testing broker connection...")
        app.control.inspect().active()
        print("✅ Broker connection successful")
    except Exception as e:
        print(f"❌ Broker connection failed: {e}")
        return False
    
    # Test result backend connection
    try:
        print("📡 Testing result backend connection...")
        app.backend.client.ping()
        print("✅ Result backend connection successful")
    except Exception as e:
        print(f"❌ Result backend connection failed: {e}")
        return False
    
    print("✅ All Celery connections successful!")
    return True

if __name__ == "__main__":
    success = test_celery_connection()
    sys.exit(0 if success else 1) 
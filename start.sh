#!/bin/bash

echo "🚀 Starting AI Rate Limiter Services..."

# Create logs directory if it doesn't exist
mkdir -p logs

# Set proper permissions for Celery Beat
chmod 777 /tmp 2>/dev/null || true

echo "✅ Environment setup complete"

# Start the application
exec "$@" 
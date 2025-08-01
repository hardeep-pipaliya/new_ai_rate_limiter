#!/bin/bash

# AI Rate Limiter Deployment Script
# For Ubuntu Server: 64.227.9.103

echo "🚀 Starting AI Rate Limiter Deployment..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs

# Set up environment variables
echo "🔧 Setting up environment variables..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration before continuing"
    echo "   - Update DATABASE_URL with your PostgreSQL credentials"
    echo "   - Update API keys for your AI providers"
    echo "   - Update server host/port if needed"
    read -p "Press Enter after editing .env file..."
fi

# Create APISIX config directory
echo "🔧 Creating APISIX configuration..."
mkdir -p apisix_config

# Build and start services
echo "🐳 Building and starting services..."
docker-compose build
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service status
echo "🔍 Checking service status..."
docker-compose ps

# Initialize database
echo "🗄️  Initializing database..."
docker-compose exec flask_app flask db upgrade

echo "✅ Deployment completed!"
echo ""
echo "🌐 Services available at:"
echo "   - Flask App: http://64.227.9.103:8501"
echo "   - APISIX Dashboard: http://64.227.9.103:9000"
echo "   - RabbitMQ Management: http://64.227.9.103:15672"
echo ""
echo "📊 Monitor logs with:"
echo "   docker-compose logs -f"
echo ""
echo "🔄 To restart services:"
echo "   docker-compose restart"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose down" 
#!/bin/bash

# AI Rate Limiter Server Startup Script
# For Ubuntu Server 64.227.9.103

echo "🚀 Starting AI Rate Limiter on Ubuntu Server..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Installing Docker..."
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    sudo usermod -aG docker $USER
    echo "✅ Docker installed successfully"
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed successfully"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p apisix_config

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp env.example .env
    echo "✅ .env file created"
fi

# Update .env file with server IP
echo "🌐 Updating configuration for server IP: 64.227.9.103"
sed -i 's/localhost/64.227.9.103/g' .env

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service status
echo "📊 Checking service status..."
docker-compose ps

# Initialize database
echo "🗄️ Initializing database..."
docker-compose exec flask_app flask db upgrade

# Show service URLs
echo ""
echo "🎉 AI Rate Limiter is now running!"
echo ""
echo "📋 Service URLs:"
echo "   Flask API: http://64.227.9.103:8501"
echo "   APISIX Dashboard: http://64.227.9.103:9000"
echo "   RabbitMQ Management: http://64.227.9.103:15672 (guest/guest)"
echo ""
echo "🔧 Test the API:"
echo "   curl -X POST http://64.227.9.103:8501/message/create \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"queue_id\": \"test-queue\", \"prompt\": \"Hello world\"}'"
echo ""
echo "📊 Monitor logs:"
echo "   docker-compose logs -f flask_app"
echo "   docker-compose logs -f celery_worker"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose down" 
# Ubuntu Server Deployment Guide
## For Server: 64.227.9.103

This guide will help you deploy the AI Rate Limiter on your Ubuntu server with APISIX rate limiting.

## 🚀 Quick Start

### Step 1: Connect to Your Server
```bash
ssh root@64.227.9.103
```

### Step 2: Clone/Upload the Project
```bash
# If you have git access
git clone <your-repo-url>
cd ai_rate_limiter_new

# Or upload files via SCP/SFTP
```

### Step 3: Make the Startup Script Executable
```bash
chmod +x start_server.sh
```

### Step 4: Run the Startup Script
```bash
./start_server.sh
```

## 🔧 Manual Setup (Alternative)

### Step 1: Install Docker and Docker Compose
```bash
# Update system
sudo apt-get update

# Install Docker
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 2: Create Environment File
```bash
cp env.example .env
```

### Step 3: Update Configuration for Server IP
```bash
# Update .env file to use server IP instead of localhost
sed -i 's/localhost/64.227.9.103/g' .env
```

### Step 4: Start Services
```bash
# Create necessary directories
mkdir -p logs
mkdir -p apisix_config

# Start all services
docker-compose up -d --build

# Wait for services to be ready
sleep 30

# Initialize database
docker-compose exec flask_app flask db upgrade
```

## 📋 Service URLs

Once deployed, you can access:

- **Flask API**: http://64.227.9.103:8501
- **APISIX Dashboard**: http://64.227.9.103:9000
- **RabbitMQ Management**: http://64.227.9.103:15672 (guest/guest)
- **PostgreSQL**: 64.227.9.103:5432
- **Redis**: 64.227.9.103:6379

## 🔧 APISIX Rate Limiting Configuration

The APISIX configuration includes:

### Rate Limiting Plugins:
1. **limit-req**: Request rate limiting (10 req/sec, burst 20)
2. **limit-conn**: Connection limiting (10 connections, burst 20)
3. **limit-count**: Request count limiting (100 requests per 60 seconds)

### Supported AI Providers:
- **OpenAI**: `/v1/chat/completions`
- **Azure OpenAI**: `/v1/chat/completions/azure`
- **Anthropic Claude**: `/v1/chat/completions/anthropic`
- **DeepSeek**: `/v1/chat/completions/deepseek`

## 🧪 Testing the Deployment

### 1. Create a Queue and Provider
```bash
curl -X POST http://64.227.9.103:8501/queue/create \
  -H "Content-Type: application/json" \
  -d '{
    "queue_id": "test-queue-123",
    "providers": [
      {
        "provider_name": "OpenAI",
        "provider_type": "openai",
        "api_key": "sk-your-api-key",
        "limit": 1000,
        "time_window": 3600,
        "config": {
          "model": "gpt-4o",
          "endpoint": "https://api.openai.com"
        }
      }
    ]
  }'
```

### 2. Test Single Message Creation
```bash
curl -X POST http://64.227.9.103:8501/message/create \
  -H "Content-Type: application/json" \
  -d '{
    "queue_id": "test-queue-123",
    "prompt": "Hello, this is a test message"
  }'
```

### 3. Test Batch Message Creation
```bash
curl -X POST http://64.227.9.103:8501/message/create \
  -H "Content-Type: application/json" \
  -d '{
    "queue_id": "test-queue-123",
    "messages": [
      {"prompt": "First message in batch"},
      {"prompt": "Second message in batch"},
      {"prompt": "Third message in batch"}
    ]
  }'
```

## 📊 Monitoring

### Check Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# Flask app logs
docker-compose logs -f flask_app

# Celery worker logs
docker-compose logs -f celery_worker

# APISIX logs
docker-compose logs -f apisix
```

### Monitor APISIX Dashboard
- Open http://64.227.9.103:9000
- Default credentials: admin/admin

## 🔧 Troubleshooting

### Common Issues:

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   sudo netstat -tulpn | grep :8501
   
   # Kill the process if needed
   sudo kill -9 <PID>
   ```

2. **Docker Permission Issues**
   ```bash
   # Add user to docker group
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **Service Not Starting**
   ```bash
   # Check logs
   docker-compose logs <service_name>
   
   # Restart specific service
   docker-compose restart <service_name>
   ```

4. **Database Connection Issues**
   ```bash
   # Restart database
   docker-compose restart postgres
   
   # Reinitialize database
   docker-compose exec flask_app flask db upgrade
   ```

### Reset Everything
```bash
# Stop and remove all containers and volumes
docker-compose down -v

# Remove all images
docker system prune -a

# Start fresh
./start_server.sh
```

## 🔒 Security Considerations

1. **Change Default Passwords**
   - Update PostgreSQL password
   - Update RabbitMQ credentials
   - Update APISIX admin key

2. **Firewall Configuration**
   ```bash
   # Allow only necessary ports
   sudo ufw allow 22    # SSH
   sudo ufw allow 8501  # Flask API
   sudo ufw allow 9000  # APISIX Dashboard
   sudo ufw enable
   ```

3. **SSL/HTTPS Setup**
   - Consider setting up SSL certificates
   - Use reverse proxy (nginx) for HTTPS

## 📈 Performance Optimization

1. **Resource Limits**
   - Adjust Docker memory limits
   - Configure Redis memory settings
   - Optimize PostgreSQL settings

2. **Scaling**
   - Scale Celery workers: `docker-compose up --scale celery_worker=3`
   - Add more APISIX instances
   - Use Redis cluster for high availability

## 🆘 Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify service status: `docker-compose ps`
3. Test connectivity: `curl http://64.227.9.103:8501/health`
4. Check APISIX dashboard: http://64.227.9.103:9000 
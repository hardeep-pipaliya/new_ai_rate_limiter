# AI Rate Limiter

A comprehensive Flask-based AI rate limiting and batch processing system with Redis caching, RabbitMQ queuing, and PostgreSQL persistence.

## 🚀 Features

- **Dynamic Queue Management**: Create and manage message queues with multiple AI providers
- **Rate Limiting**: Configurable rate limits per provider with Redis-based tracking
- **Batch Processing**: Process large batches of messages with progress tracking
- **Direct Provider Integration**: Direct integration with OpenAI, Anthropic, and DeepSeek APIs
- **Webhook Support**: Real-time notifications for batch completion
- **Multiple AI Providers**: Support for OpenAI, Azure, Anthropic, DeepSeek, and Claude
- **Worker Management**: Dynamic Celery worker creation and monitoring
- **Export Options**: CSV and JSON export for batch results
- **Docker Support**: Complete containerized deployment

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask App     │    │   RabbitMQ      │    │   Celery        │
│   (API Layer)   │───▶│   (Message      │───▶│   Workers       │
│                 │    │   Queue)        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   Redis         │    │   APISIX        │
│   (Database)    │    │   (Cache &      │    │   (API Gateway) │
│                 │    │   Counters)     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Git

## 🛠️ Installation

### Option 1: Docker Deployment (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai_rate_limiter.git
   cd ai_rate_limiter
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Initialize the database**
   ```bash
   docker-compose exec flask_app flask db upgrade
   ```

### Option 2: Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai_rate_limiter.git
   cd ai_rate_limiter
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Start required services** (PostgreSQL, Redis, RabbitMQ, APISIX)

6. **Run the application**
   ```bash
   python run.py
   ```

7. **Run Celery worker** (in another terminal)
   ```bash
   celery -A app.celery worker --loglevel=info
   ```

## 🚀 Quick Start

### 1. Create a Queue with Providers

```bash
curl -X POST http://localhost:8501/queue/create \
  -H "Content-Type: application/json" \
  -d '{
    "queue_id": "my-queue-123",
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

### 2. Create a Single Message

```bash
curl -X POST http://localhost:8501/message/create \
  -H "Content-Type: application/json" \
  -d '{
    "queue_id": "my-queue-123",
    "prompt": "Hello, this is a test message"
  }'
```

### 3. Create a Batch of Messages

```bash
curl -X POST http://localhost:8501/message/create \
  -H "Content-Type: application/json" \
  -d '{
    "queue_id": "my-queue-123",
    "messages": [
      {"prompt": "First message in batch"},
      {"prompt": "Second message in batch"},
      {"prompt": "Third message in batch"}
    ],
    "webhook_url": "https://your-webhook.com/batch-complete",
    "webhook_event": "on_complete"
  }'
```

### 4. Get Batch Results

```bash
# Get results as JSON
curl http://localhost:8501/batch/{batch_id}/results

# Get results as CSV
curl http://localhost:8501/batch/{batch_id}/results?format=csv
```

## 📊 API Endpoints

### Queue Management
- `POST /queue/create` - Create a new queue with providers
- `GET /queues` - List all queues
- `GET /queue/{queue_id}` - Get queue details
- `DELETE /queue/{queue_id}` - Delete a queue

### Message Management
- `POST /message/create` - Create single message or batch of messages
- `GET /message/read/{message_id}` - Get message details
- `DELETE /message/delete/{message_id}` - Delete a message

### Batch Management
- `GET /batch/{batch_id}/messages` - Get all messages in a batch
- `GET /batch/{batch_id}/results` - Get batch results (JSON/CSV)

### Provider Management
- `POST /provider/create` - Create a new provider
- `GET /providers` - List all providers
- `PATCH /provider/update/{provider_id}` - Update a provider
- `DELETE /provider/delete/{provider_id}` - Delete a provider

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `env.example`:

```bash
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/ai_rate_limiter

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# RabbitMQ Configuration
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# API Gateway Configuration
APISIX_GATEWAY_URL=http://localhost:9080
APISIX_ADMIN_URL=http://localhost:9180

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8501
```

### APISIX Rate Limiting

The system uses APISIX for rate limiting with the following plugins:

- **limit-req**: Request rate limiting (10 req/sec, burst 20)
- **limit-conn**: Connection limiting (10 connections, burst 20)
- **limit-count**: Request count limiting (100 requests per 60 seconds)

## 🐳 Docker Deployment

### Production Deployment

```bash
# Use production docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

### Custom Deployment

```bash
# Build and start services
docker-compose up -d --build

# Scale workers
docker-compose up --scale celery_worker=3

# View logs
docker-compose logs -f flask_app
```

## 📈 Monitoring

### Service URLs (Docker)
- **Flask API**: http://localhost:8501
- **APISIX Dashboard**: http://localhost:9000
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### Health Checks

```bash
# Check API health
curl http://localhost:8501/health

# Check service status
docker-compose ps
```

## 🧪 Testing

### Run Test Script

```bash
python test_new_workflow.py
```

### Manual Testing

```bash
# Test single message creation
curl -X POST http://localhost:8501/message/create \
  -H "Content-Type: application/json" \
  -d '{
    "queue_id": "test-queue-123",
    "prompt": "Hello world"
  }'

# Test batch message creation
curl -X POST http://localhost:8501/message/create \
  -H "Content-Type: application/json" \
  -d '{
    "queue_id": "test-queue-123",
    "messages": [
      {"prompt": "First message"},
      {"prompt": "Second message"}
    ]
  }'
```

## 🔒 Security

### Default Credentials
- **RabbitMQ**: guest/guest
- **PostgreSQL**: postgres/postgres
- **APISIX Dashboard**: admin/admin

### Security Recommendations
1. Change default passwords
2. Use SSL/TLS in production
3. Configure firewall rules
4. Use environment variables for secrets
5. Enable authentication for all services

## 🚀 Deployment

### Ubuntu Server Deployment

For deployment on Ubuntu servers, see [UBUNTU_DEPLOYMENT.md](UBUNTU_DEPLOYMENT.md).

### Cloud Deployment

The system is designed to work with:
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- Kubernetes

## 📚 Documentation

- [Workflow Changes](WORKFLOW_CHANGES.md) - Recent workflow updates
- [Ubuntu Deployment](UBUNTU_DEPLOYMENT.md) - Server deployment guide
- [API Documentation](swagger_apisix.yaml) - OpenAPI specification

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues:

1. Check the logs: `docker-compose logs -f`
2. Verify service status: `docker-compose ps`
3. Test connectivity: `curl http://localhost:8501/health`
4. Check APISIX dashboard: http://localhost:9000

## 🙏 Acknowledgments

- [APISIX](https://apisix.apache.org/) - API Gateway
- [Celery](https://celeryproject.org/) - Task Queue
- [Flask](https://flask.palletsprojects.com/) - Web Framework
- [Redis](https://redis.io/) - Cache and Message Broker
- [RabbitMQ](https://www.rabbitmq.com/) - Message Queue
- [PostgreSQL](https://www.postgresql.org/) - Database 
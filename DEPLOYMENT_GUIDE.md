# AI Rate Limiter - Production Deployment Guide

## 🚀 Quick Start

### 1. Prerequisites
- Docker and Docker Compose installed
- Git (to clone the repository)

### 2. Setup Environment
```bash
# Copy environment template
cp env.example .env

# Edit the .env file with your configuration
nano .env
```

**Important**: Update these values in `.env`:
- `SECRET_KEY`: Generate a secure random key
- `POSTGRES_PASSWORD`: Set a strong database password
- `DATABASE_URL`: Update with your password

### 3. Deploy Services
```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### 4. Verify Deployment
```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# Run health check
python health_check.py
```

## 📋 Services Overview

| Service | Port | Description |
|---------|------|-------------|
| Flask App | 8501 | Main application |
| APISIX Gateway | 9080 | API Gateway |
| APISIX Admin | 9180 | APISIX Admin API |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache/Queue |
| RabbitMQ | 5672 | Message Queue |
| RabbitMQ Management | 15672 | RabbitMQ Web UI |

## 🔧 Configuration

### APISIX Configuration
- **Standalone Mode**: No etcd required
- **Rate Limiting**: Configured in `apisix_config/config.yaml`
- **Admin Key**: `edd1c9f034335f136f87ad84b625c8f1`

### Environment Variables
All configuration is done through the `.env` file. Key variables:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `RABBITMQ_URL`: RabbitMQ connection string
- `CELERY_BROKER_URL`: Celery broker URL
- `APISIX_GATEWAY_URL`: APISIX gateway URL
- `SECRET_KEY`: Flask secret key

## 🛠️ Management Commands

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f flask_app
```

### Restart Services
```bash
# All services
docker-compose -f docker-compose.prod.yml restart

# Specific service
docker-compose -f docker-compose.prod.yml restart flask_app
```

### Stop Services
```bash
docker-compose -f docker-compose.prod.yml down
```

### Update and Redeploy
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up --build -d
```

## 🔍 Troubleshooting

### Common Issues

1. **APISIX fails to start**
   - Check if `apisix_config/config.yaml` exists
   - Verify file permissions

2. **Database connection errors**
   - Ensure PostgreSQL container is running
   - Check `DATABASE_URL` in `.env`

3. **Celery worker issues**
   - Check RabbitMQ connection
   - Verify `CELERY_BROKER_URL`

4. **Port conflicts**
   - Check if ports are already in use
   - Modify ports in `docker-compose.prod.yml`

### Debug Commands
```bash
# Check container status
docker-compose -f docker-compose.prod.yml ps

# Check container logs
docker-compose -f docker-compose.prod.yml logs apisix

# Access container shell
docker-compose -f docker-compose.prod.yml exec flask_app bash
```

## 📊 Monitoring

### Health Check
```bash
python health_check.py
```

### Service Status
```bash
docker-compose -f docker-compose.prod.yml ps
```

### Resource Usage
```bash
docker stats
```

## 🔒 Security Notes

1. **Change default passwords** in `.env`
2. **Use strong SECRET_KEY**
3. **Restrict network access** in production
4. **Enable SSL/TLS** for production use
5. **Regular security updates**

## 📝 API Endpoints

### Flask App (Port 8501)
- `GET /api/queues/` - List queues
- `GET /api/providers/` - List providers
- `POST /api/messages/` - Create message
- `GET /api/workers/` - List workers

### APISIX Gateway (Port 9080)
- All Flask app endpoints proxied through APISIX
- Rate limiting applied automatically

## 🆘 Support

If you encounter issues:
1. Check the logs: `docker-compose -f docker-compose.prod.yml logs -f`
2. Run health check: `python health_check.py`
3. Verify environment variables in `.env`
4. Check Docker container status 
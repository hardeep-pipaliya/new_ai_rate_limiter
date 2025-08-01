# APISIX Rate Limiting Configuration

This document explains how APISIX is configured to provide rate limiting for all 5 AI providers in the AI Rate Limiter system.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask App     │    │   APISIX        │    │   AI Providers  │
│   (API Layer)   │───▶│   (Rate Limiting│───▶│   (OpenAI,      │
│                 │    │   & Gateway)    │    │   Claude, etc.) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📊 Supported AI Providers

The system supports 5 major AI providers with individual rate limiting:

1. **OpenAI** - GPT models (GPT-3.5, GPT-4, GPT-4o)
2. **Azure OpenAI** - Microsoft's Azure-hosted OpenAI models
3. **Anthropic Claude** - Claude models (Claude-3-Sonnet, Claude-3-Haiku)
4. **DeepSeek** - DeepSeek Chat models
5. **Google Cloud AI** - Gemini models (Gemini Pro, Gemini Flash)

## 🔧 APISIX Configuration

### Rate Limiting Plugins

APISIX uses three rate limiting plugins for each provider:

#### 1. **limit-req** (Request Rate Limiting)
- **Rate**: 10 requests per second
- **Burst**: 20 requests
- **Key**: Remote IP address
- **Rejected Code**: 429 (Too Many Requests)

#### 2. **limit-conn** (Connection Limiting)
- **Connections**: 10 concurrent connections
- **Burst**: 20 connections
- **Key**: Remote IP address
- **Rejected Code**: 429

#### 3. **limit-count** (Request Count Limiting)
- **Count**: 100 requests per 60 seconds
- **Time Window**: 60 seconds
- **Key**: Remote IP address
- **Rejected Code**: 429

### Provider-Specific Endpoints

Each provider has its own APISIX endpoint with rate limiting:

```
/v1/chat/completions/openai     → api.openai.com/v1/chat/completions
/v1/chat/completions/azure      → {AZURE_ENDPOINT}/openai/deployments/*/chat/completions
/v1/chat/completions/anthropic  → api.anthropic.com/v1/messages
/v1/chat/completions/deepseek   → api.deepseek.com/v1/chat/completions
/v1/chat/completions/google     → {GOOGLE_ENDPOINT}/v1/models/*:generateContent
```

## 🚀 Usage Examples

### 1. Create a Queue with OpenAI Provider

```bash
curl -X POST http://localhost:8501/api/v1/queue/create \
  -H "Content-Type: application/json" \
  -d '{
    "queue_name": "openai-queue",
    "provider_type": "openai",
    "config": {
      "api_key": "sk-your-openai-key",
      "model": "gpt-4o"
    }
  }'
```

### 2. Create a Message (Goes Through APISIX)

```bash
curl -X POST http://localhost:8501/api/v1/message/create \
  -H "Content-Type: application/json" \
  -d '{
    "queue_id": "openai-queue-id",
    "prompt": "Hello, how are you?",
    "system_prompt": "You are a helpful assistant"
  }'
```

### 3. Direct APISIX Testing

```bash
# Test OpenAI endpoint with rate limiting
curl -X POST http://localhost:9080/v1/chat/completions/openai \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-your-key" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## 📈 Monitoring

### APISIX Dashboard
- **URL**: http://localhost:9180
- **Admin Key**: `edd1c9f034335f136f87ad84b625c8f1`

### Rate Limiting Metrics
- Monitor rate limiting in real-time
- View rejected requests (429 responses)
- Track request patterns per IP

### Health Checks

```bash
# Check APISIX health
curl http://localhost:9180/apisix/admin/services

# Check rate limiting status
curl http://localhost:9180/apisix/admin/plugins
```

## 🔒 Security Features

### 1. **IP-based Rate Limiting**
- Each client IP is tracked separately
- Prevents abuse from single sources

### 2. **Provider Isolation**
- Each AI provider has separate rate limits
- Prevents one provider from affecting others

### 3. **Burst Protection**
- Allows temporary burst of requests
- Prevents sudden traffic spikes

### 4. **Connection Limiting**
- Limits concurrent connections
- Prevents resource exhaustion

## 🛠️ Configuration Files

### 1. **APISIX Config** (`apisix_config/config.yaml`)
```yaml
apisix:
  node_listen: 9080
  enable_admin: true
  admin_listen:
    port: 9180
  allow_admin:
    - 0.0.0.0/0
  admin_key:
    - key: edd1c9f034335f136f87ad84b625c8f1
      role: admin
```

### 2. **Routes Config** (`apisix_config/routes.yaml`)
- Contains all provider-specific routes
- Defines rate limiting rules
- Configures proxy settings

## 🧪 Testing

### Run Comprehensive Tests
```bash
python test_all_providers.py
```

This script tests:
- Health checks for Flask and APISIX
- Queue creation for all 5 providers
- Message creation through APISIX
- Rate limiting functionality

### Manual Rate Limiting Test
```bash
# Make multiple rapid requests to trigger rate limiting
for i in {1..15}; do
  curl -X POST http://localhost:9080/v1/chat/completions/openai \
    -H "Content-Type: application/json" \
    -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"test"}]}'
  echo "Request $i"
done
```

## 🔧 Troubleshooting

### Common Issues

1. **APISIX Not Starting**
   ```bash
   # Check APISIX logs
   docker-compose logs apisix
   
   # Verify config files exist
   ls -la apisix_config/
   ```

2. **Rate Limiting Not Working**
   ```bash
   # Check APISIX admin API
   curl http://localhost:9180/apisix/admin/routes
   
   # Verify plugins are loaded
   curl http://localhost:9180/apisix/admin/plugins
   ```

3. **Provider Connection Issues**
   ```bash
   # Test direct provider connection
   curl -X POST https://api.openai.com/v1/chat/completions \
     -H "Authorization: Bearer YOUR_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"test"}]}'
   ```

### Logs to Monitor

```bash
# APISIX logs
docker-compose logs -f apisix

# Flask app logs
docker-compose logs -f flask_app

# Celery worker logs
docker-compose logs -f celery_worker
```

## 📊 Performance Tuning

### Rate Limiting Adjustments

For high-traffic scenarios, adjust the rate limits in `apisix_config/routes.yaml`:

```yaml
limit-req:
  rate: 50        # Increase from 10 to 50 req/sec
  burst: 100      # Increase from 20 to 100
```

### Provider-Specific Limits

Different providers have different rate limits:

- **OpenAI**: 3,500 requests per minute
- **Azure**: 1,000 requests per minute
- **Anthropic**: 5,000 requests per minute
- **DeepSeek**: 1,000 requests per minute
- **Google**: 1,500 requests per minute

## 🚀 Deployment

### Production Considerations

1. **SSL/TLS**: Use HTTPS in production
2. **Authentication**: Add API key authentication
3. **Monitoring**: Set up alerts for rate limiting
4. **Scaling**: Use multiple APISIX instances
5. **Backup**: Regular configuration backups

### Environment Variables

```bash
# Required for APISIX
APISIX_GATEWAY_URL=http://apisix:9080
APISIX_ADMIN_URL=http://apisix:9180

# Provider-specific (optional)
AZURE_OPENAI_ENDPOINT=your-azure-endpoint
GOOGLE_CLOUD_ENDPOINT=your-google-endpoint
```

This setup provides robust rate limiting for all 5 AI providers while maintaining high availability and performance. 
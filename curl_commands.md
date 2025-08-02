# AI Rate Limiter - Curl Commands for Testing

Base URL: `http://64.227.9.103:8501` (or `http://localhost:8501` for local testing)

## 🔧 Queue Management

### Create Queue
```bash
curl -X POST http://64.227.9.103:8501/api/v1/queue/create \
  -H 'Content-Type: application/json' \
  -d '{
    "queue_id": "test_queue_1",
    "providers": [
      {
        "provider_name": "openai_gpt4",
        "provider_type": "openai",
        "api_key": "sk-test-key-123",
        "limit": 100,
        "time_window": 3600,
        "config": {
          "model": "gpt-4",
          "max_tokens": 1000
        }
      }
    ]
  }'
```

### Get All Queues
```bash
curl -X GET http://64.227.9.103:8501/api/v1/queues/
```

### Get Specific Queue
```bash
curl -X GET http://64.227.9.103:8501/api/v1/queue/test_queue_1
```

### Delete Queue
```bash
curl -X DELETE http://64.227.9.103:8501/api/v1/queue/delete/test_queue_1
```

## 🔧 Provider Management

### Get All Providers
```bash
curl -X GET http://64.227.9.103:8501/api/v1/providers
```

### Get Providers for Queue
```bash
curl -X GET 'http://64.227.9.103:8501/api/v1/providers?queue_id=test_queue_1'
```

### Create Provider
```bash
curl -X POST http://64.227.9.103:8501/api/v1/provider/create \
  -H 'Content-Type: application/json' \
  -d '{
    "queue_id": "test_queue_1",
    "provider_name": "anthropic_claude",
    "provider_type": "anthropic",
    "api_key": "sk-ant-test-key-456",
    "limit": 50,
    "time_window": 3600,
    "config": {
      "model": "claude-3-sonnet-20240229"
    }
  }'
```

### Update Provider
```bash
curl -X PATCH http://64.227.9.103:8501/api/v1/provider/update/1 \
  -H 'Content-Type: application/json' \
  -d '{
    "limit": 150,
    "time_window": 7200
  }'
```

### Delete Provider
```bash
curl -X DELETE http://64.227.9.103:8501/api/v1/provider/delete/1
```

## 🔧 Worker Management

### Create Workers
```bash
curl -X POST http://64.227.9.103:8501/api/v1/worker/create/test_queue_1 \
  -H 'Content-Type: application/json' \
  -d '{
    "count": 2
  }'
```

### Get Worker Logs
```bash
curl -X GET http://64.227.9.103:8501/api/v1/worker/logs/1
```

### Delete Worker
```bash
curl -X DELETE http://64.227.9.103:8501/api/v1/worker/delete/1
```

## 🔧 Message Management

### Create Single Message
```bash
curl -X POST http://64.227.9.103:8501/api/v1/message/create \
  -H 'Content-Type: application/json' \
  -d '{
    "queue_id": "test_queue_1",
    "prompt": "Hello, this is a single test message",
    "system_prompt": "You are a helpful assistant",
    "supportive_variable": {
      "test": "single_message",
      "priority": "high"
    }
  }'
```

### Create Batch Messages
```bash
curl -X POST http://64.227.9.103:8501/api/v1/message/create \
  -H 'Content-Type: application/json' \
  -d '{
    "queue_id": "test_queue_1",
    "messages": [
      {
        "prompt": "First message in batch",
        "system_prompt": "You are a helpful assistant",
        "supportive_variable": {
          "test": "batch1",
          "order": 1
        }
      },
      {
        "prompt": "Second message in batch",
        "system_prompt": "You are a helpful assistant",
        "supportive_variable": {
          "test": "batch2",
          "order": 2
        }
      },
      {
        "prompt": "Third message in batch",
        "system_prompt": "You are a helpful assistant",
        "supportive_variable": {
          "test": "batch3",
          "order": 3
        }
      }
    ],
    "webhook_url": "https://example.com/webhook",
    "webhook_event": "on_complete"
  }'
```

### Read Message
```bash
curl -X GET http://64.227.9.103:8501/api/v1/message/read/1
```

### Delete Message
```bash
curl -X DELETE http://64.227.9.103:8501/api/v1/message/delete/1
```

### Get Batch Messages
```bash
curl -X GET http://64.227.9.103:8501/api/v1/batch/1/messages
```

### Get Batch Results (JSON)
```bash
curl -X GET 'http://64.227.9.103:8501/api/v1/batch/1/results?format=json'
```

### Get Batch Results (CSV)
```bash
curl -X GET 'http://64.227.9.103:8501/api/v1/batch/1/results?format=csv'
```

## 🔧 Error Testing

### Test Invalid Queue
```bash
curl -X POST http://64.227.9.103:8501/api/v1/message/create \
  -H 'Content-Type: application/json' \
  -d '{
    "queue_id": "non_existent_queue",
    "prompt": "This should fail"
  }'
```

### Test Missing Fields
```bash
curl -X POST http://64.227.9.103:8501/api/v1/message/create \
  -H 'Content-Type: application/json' \
  -d '{
    "queue_id": "test_queue_1"
  }'
```

### Test Non-existent Message
```bash
curl -X GET http://64.227.9.103:8501/api/v1/message/read/999999
```

## 🔧 Quick Test Sequence

Here's a quick test sequence to verify everything works:

```bash
# 1. Create a queue
curl -X POST http://64.227.9.103:8501/api/v1/queue/create \
  -H 'Content-Type: application/json' \
  -d '{
    "queue_id": "quick_test",
    "providers": [
      {
        "provider_name": "test_provider",
        "provider_type": "openai",
        "api_key": "sk-test-123",
        "limit": 10,
        "time_window": 3600
      }
    ]
  }'

# 2. Create a single message
curl -X POST http://64.227.9.103:8501/api/v1/message/create \
  -H 'Content-Type: application/json' \
  -d '{
    "queue_id": "quick_test",
    "prompt": "Test message"
  }'

# 3. Create batch messages
curl -X POST http://64.227.9.103:8501/api/v1/message/create \
  -H 'Content-Type: application/json' \
  -d '{
    "queue_id": "quick_test",
    "messages": [
      {"prompt": "Batch message 1"},
      {"prompt": "Batch message 2"}
    ]
  }'

# 4. Check queues
curl -X GET http://64.227.9.103:8501/api/v1/queues/

# 5. Check providers
curl -X GET http://64.227.9.103:8501/api/v1/providers
```

## 📊 Service URLs

- **Flask API**: http://64.227.9.103:8501
- **Flask App**: http://64.227.9.103:8501
- **APISIX Gateway**: http://64.227.9.103:9080
- **APISIX Admin**: http://64.227.9.103:9180
- **RabbitMQ Management**: http://64.227.9.103:15672
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 🚀 Running the Complete Test Script

To run the comprehensive test script:

```bash
# Make the script executable
chmod +x test_all_endpoints.sh

# Run the test script
./test_all_endpoints.sh
```

## 💡 Tips

1. **Check if services are running**:
   ```bash
   docker-compose ps
   ```

2. **View logs**:
   ```bash
   docker-compose logs -f flask_app
   ```

3. **Initialize database**:
   ```bash
   docker-compose exec flask_app flask db upgrade
   ```

4. **Test with real API keys**:
   Replace the test API keys with real ones for actual AI provider testing.

5. **Monitor APISIX**:
Check the APISIX dashboard at http://64.227.9.103:9180 for rate limiting configuration. 
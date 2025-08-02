# Workflow Changes Summary

## Overview
This document outlines the changes made to implement the new workflow where:
1. **Single endpoint** `/message/create` handles both single messages and batch messages
2. **Single messages** get individual `batch_id` and `message_id`
3. **Batch messages** share the same `batch_id` but have different `message_id`s
4. Rate limiting is handled by APISIX, not Redis
5. Redis only stores messages and counts requests/responses

## Changes Made

### 1. Message Routes (`app/routes/message_routes.py`)
- ✅ **Updated** `/message/create` endpoint to handle both single and batch messages
- ✅ **Single message**: Uses `prompt` field
- ✅ **Batch messages**: Uses `messages` array field
- ✅ **Kept** all other endpoints for message management

### 2. Message Service (`app/services/message_service.py`)
- ✅ **Updated** `create_message()` method for single messages:
  - Generate unique `batch_id` and `message_id` for each message
  - Create a batch entry with `request_count=1`
  - Initialize Redis counters for the batch
  - Return both `batch_id` and `message_id` in response
- ✅ **Added** `create_batch_messages()` method for batch messages:
  - Generate single `batch_id` for all messages in batch
  - Generate unique `message_id` for each message in batch
  - Create batch entry with `request_count=len(messages)`
  - Initialize Redis counters for the batch
  - Return `batch_id` and list of `message_ids`

### 3. Redis Service (`app/services/redis_service.py`)
- ✅ **Removed** all rate limiting methods:
  - `set_rate_limit()`
  - `check_rate_limit()`
  - `decrement_rate_limit()`
- ✅ **Kept** message storage and batch counting functionality:
  - `init_batch_counters()`
  - `increment_batch_response()`
  - `get_batch_counters()`
  - `store_message_result()`
  - `get_message_result()`
  - `store_batch_results()`
  - `get_batch_results()`

### 4. Worker Tasks (`app/tasks/worker_tasks.py`)
- ✅ **Removed** rate limiting logic from `process_message()`:
  - No more `RedisService.check_rate_limit()` calls
  - No more `RedisService.decrement_rate_limit()` calls
- ✅ **Kept** batch completion logic:
  - Still increments batch response counter
  - Still publishes to aggregator queue when batch is complete

### 5. APISIX Service (`app/services/apisix_service.py`)
- ✅ **Removed** `configure_rate_limit()` method
- ✅ **Kept** all other APISIX functionality for API gateway integration

## New Workflow

### Single Message Creation Flow
1. **User calls** `/message/create` with `prompt` field
2. **System generates** unique `batch_id` and `message_id`
3. **Database entries created**:
   - New batch record with `request_count=1`
   - New message record with generated IDs
4. **Redis initialized** with batch counters (`req.count=1`, `res.count=0`)
5. **Message queued** in RabbitMQ for processing
6. **Response returned** with both `batch_id` and `message_id`

### Batch Message Creation Flow
1. **User calls** `/message/create` with `messages` array field
2. **System generates** single `batch_id` for all messages
3. **System generates** unique `message_id` for each message
4. **Database entries created**:
   - New batch record with `request_count=len(messages)`
   - Multiple message records with same `batch_id` but different `message_id`s
5. **Redis initialized** with batch counters (`req.count=N`, `res.count=0`)
6. **Messages queued** in RabbitMQ for processing
7. **Response returned** with `batch_id` and list of `message_ids`

### Message Processing Flow
1. **Worker picks up** message from RabbitMQ
2. **Worker sends** request to APISIX (rate limiting handled by APISIX)
3. **APISIX returns** response to worker
4. **Worker stores** response in Redis and database
5. **Worker increments** batch response counter in Redis
6. **If batch complete** (req.count == res.count), worker publishes to aggregator queue

### Batch Completion Flow
1. **Aggregator worker** picks up batch completion message
2. **Worker retrieves** all messages for the batch from database
3. **Worker aggregates** results and stores in Redis
4. **Batch status** updated to 'completed' in database
5. **Webhook sent** if configured

## API Endpoints

### Single Message Creation
```bash
POST /message/create
{
  "queue_id": "queue-123",
  "prompt": "Hello world",
  "system_prompt": "You are helpful",
  "supportive_variable": {"key": "value"}
}

Response:
{
  "success": true,
  "message": "Message created successfully",
  "batch_id": "uuid-1",
  "message_id": "uuid-2"
}
```

### Batch Message Creation
```bash
POST /message/create
{
  "queue_id": "queue-123",
  "messages": [
    {
      "prompt": "First message",
      "system_prompt": "You are helpful"
    },
    {
      "prompt": "Second message",
      "system_prompt": "You are helpful"
    }
  ],
  "webhook_url": "https://example.com/webhook",
  "webhook_event": "on_complete"
}

Response:
{
  "success": true,
  "message": "Batch created successfully",
  "batch_id": "uuid-1",
  "message_count": 2,
  "message_ids": ["uuid-2", "uuid-3"]
}
```

## Database Schema
- **Messages table**: Each message has `batch_id` and unique `message_id`
- **Batches table**: Each batch has `request_count` and `response_count`

## Redis Usage
- **Message storage**: `message:{message_id}` → message result
- **Batch counters**: `batch:{batch_id}` → `{req.count: N, res.count: 0}`
- **Batch results**: `batch_results:{batch_id}` → aggregated results

## Testing
Updated test script `test_new_workflow.py` now tests:
- Single message creation with individual batch_id and message_id
- Batch message creation with shared batch_id but different message_ids
- Message retrieval
- Batch messages retrieval

## Benefits
1. **Single endpoint**: One endpoint handles both single and batch messages
2. **Clear ID structure**: Single messages get individual IDs, batch messages share batch_id
3. **No rate limiting complexity**: Handled by APISIX
4. **Clear separation**: Redis for storage/counting, APISIX for rate limiting
5. **Easier tracking**: Each message can be tracked individually or as part of a batch

## Migration Notes
- Existing batch endpoints still work for retrieving batch data
- Rate limiting is now handled entirely by APISIX configuration
- No changes needed to database schema
- Backward compatible with existing message retrieval endpoints 
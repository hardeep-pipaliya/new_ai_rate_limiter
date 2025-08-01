#!/usr/bin/env python3
"""
Test script for the new workflow with batch_id and message_id generation
"""
import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
TEST_QUEUE_ID = "test-queue-123"

def test_create_single_message():
    """Test creating a single message with individual batch_id and message_id"""
    print("Testing single message creation...")
    
    # Create a single message
    message_data = {
        "queue_id": TEST_QUEUE_ID,
        "prompt": "Hello, this is a single test message",
        "system_prompt": "You are a helpful assistant",
        "supportive_variable": {"test": "single"}
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/message/create",
            json=message_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.json()}")
        
        if response.status_code == 201:
            result = response.json()
            if result.get('success') and 'batch_id' in result and 'message_id' in result:
                print("✅ Single message creation successful!")
                print(f"   Batch ID: {result['batch_id']}")
                print(f"   Message ID: {result['message_id']}")
                return result['batch_id'], result['message_id']
            else:
                print("❌ Single message creation failed - missing batch_id or message_id")
                return None, None
        else:
            print(f"❌ Single message creation failed with status {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error creating single message: {str(e)}")
        return None, None

def test_create_batch_messages():
    """Test creating a batch of messages with same batch_id but different message_ids"""
    print("\nTesting batch message creation...")
    
    # Create a batch of messages
    batch_data = {
        "queue_id": TEST_QUEUE_ID,
        "messages": [
            {
                "prompt": "First message in batch",
                "system_prompt": "You are a helpful assistant",
                "supportive_variable": {"test": "batch1"}
            },
            {
                "prompt": "Second message in batch",
                "system_prompt": "You are a helpful assistant",
                "supportive_variable": {"test": "batch2"}
            },
            {
                "prompt": "Third message in batch",
                "system_prompt": "You are a helpful assistant",
                "supportive_variable": {"test": "batch3"}
            }
        ],
        "webhook_url": "https://example.com/webhook",
        "webhook_event": "on_complete"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/message/create",
            json=batch_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.json()}")
        
        if response.status_code == 201:
            result = response.json()
            if result.get('success') and 'batch_id' in result and 'message_ids' in result:
                print("✅ Batch message creation successful!")
                print(f"   Batch ID: {result['batch_id']}")
                print(f"   Message Count: {result['message_count']}")
                print(f"   Message IDs: {result['message_ids']}")
                return result['batch_id'], result['message_ids']
            else:
                print("❌ Batch message creation failed - missing batch_id or message_ids")
                return None, None
        else:
            print(f"❌ Batch message creation failed with status {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error creating batch messages: {str(e)}")
        return None, None

def test_get_message(message_id):
    """Test retrieving a message"""
    print(f"\nTesting message retrieval for message_id: {message_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/message/read/{message_id}")
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Message retrieval successful!")
                data = result['data']
                print(f"   Status: {data.get('status')}")
                print(f"   Batch ID: {data.get('batch_id')}")
                print(f"   Prompt: {data.get('prompt')}")
                return True
            else:
                print("❌ Message retrieval failed")
                return False
        else:
            print(f"❌ Message retrieval failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error retrieving message: {str(e)}")
        return False

def test_get_batch_messages(batch_id):
    """Test retrieving all messages for a batch"""
    print(f"\nTesting batch messages retrieval for batch_id: {batch_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/batch/{batch_id}/messages")
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                messages = result['data']
                print(f"✅ Batch messages retrieval successful!")
                print(f"   Number of messages: {len(messages)}")
                for msg in messages:
                    print(f"   - Message ID: {msg.get('message_id')}, Status: {msg.get('status')}")
                return True
            else:
                print("❌ Batch messages retrieval failed")
                return False
        else:
            print(f"❌ Batch messages retrieval failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error retrieving batch messages: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting new workflow test...")
    print("=" * 60)
    
    # Test 1: Create a single message
    single_batch_id, single_message_id = test_create_single_message()
    
    if single_batch_id and single_message_id:
        # Test 2: Get the single message
        test_get_message(single_message_id)
        
        # Test 3: Get batch messages for single message
        test_get_batch_messages(single_batch_id)
    
    # Test 4: Create a batch of messages
    batch_id, message_ids = test_create_batch_messages()
    
    if batch_id and message_ids:
        # Test 5: Get each message in the batch
        for message_id in message_ids:
            test_get_message(message_id)
        
        # Test 6: Get all messages for the batch
        test_get_batch_messages(batch_id)
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print(f"Single Message - Batch ID: {single_batch_id}, Message ID: {single_message_id}")
        print(f"Batch Messages - Batch ID: {batch_id}, Message IDs: {message_ids}")
    else:
        print("\n❌ Tests failed - could not create messages")

if __name__ == "__main__":
    main() 
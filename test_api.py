#!/usr/bin/env python3
"""
Test script for AI Rate Limiter API
"""

import requests
import json
import sys

def test_api():
    """Test the API endpoints"""
    base_url = "http://localhost:8501"
    
    print("🧪 Testing AI Rate Limiter API")
    print("=" * 50)
    
    # Test health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test create queue
    print("\n2. Testing queue creation...")
    queue_data = {
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
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/queue/create",
            headers={'Content-Type': 'application/json'},
            json=queue_data
        )
        if response.status_code in [200, 201]:
            print("✅ Queue creation successful")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Queue creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Queue creation error: {e}")
    
    # Test get queues
    print("\n3. Testing get queues...")
    try:
        response = requests.get(f"{base_url}/api/v1/queues/")
        if response.status_code == 200:
            print("✅ Get queues successful")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Get queues failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Get queues error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API testing completed!")

if __name__ == "__main__":
    test_api() 
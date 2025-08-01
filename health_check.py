#!/usr/bin/env python3
"""
Health check script for AI Rate Limiter services
"""

import requests
import time
import sys
from urllib.parse import urljoin

def check_service(name, url, timeout=5):
    """Check if a service is responding"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code in [200, 404]:  # 404 is OK for some endpoints
            print(f"✅ {name}: {url} - Status: {response.status_code}")
            return True
        else:
            print(f"❌ {name}: {url} - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: {url} - Error: {e}")
        return False

def main():
    print("🔍 Health Check for AI Rate Limiter Services")
    print("=" * 50)
    
    services = [
        ("Flask App", "http://localhost:8501"),
            ("APISIX Gateway", "http://localhost:9080"),
    ("APISIX Admin", "http://localhost:9180"),
        ("RabbitMQ Management", "http://localhost:15672"),
    ]
    
    all_healthy = True
    
    for name, url in services:
        if not check_service(name, url):
            all_healthy = False
        time.sleep(1)  # Small delay between checks
    
    print("\n" + "=" * 50)
    if all_healthy:
        print("🎉 All services are healthy!")
        sys.exit(0)
    else:
        print("⚠️  Some services are not responding")
        print("💡 Try running: docker-compose -f docker-compose.prod.yml logs -f")
        sys.exit(1)

if __name__ == "__main__":
    main() 
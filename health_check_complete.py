#!/usr/bin/env python3
"""
Complete health check for all AI Rate Limiter services
"""
import requests
import time
import sys
import os

def check_service(name, url, timeout=5):
    """Check if a service is responding"""
    try:
        response = requests.get(url, timeout=timeout)
        print(f"✅ {name}: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ {name}: {e}")
        return False

def check_postgres():
    """Check PostgreSQL connection"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="ai_rate_limiter",
            user="postgres",
            password="postgres"
        )
        conn.close()
        print("✅ PostgreSQL: Connected successfully")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL: {e}")
        return False

def check_redis():
    """Check Redis connection"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis: Connected successfully")
        return True
    except Exception as e:
        print(f"❌ Redis: {e}")
        return False

def check_rabbitmq():
    """Check RabbitMQ connection"""
    try:
        import pika
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost', port=5672)
        )
        connection.close()
        print("✅ RabbitMQ: Connected successfully")
        return True
    except Exception as e:
        print(f"❌ RabbitMQ: {e}")
        return False

def main():
    """Run complete health check"""
    print("🧪 Complete Health Check for AI Rate Limiter")
    print("=" * 50)
    
    services = [
        ("Flask App", "http://localhost:8501/health"),
        ("APISIX Gateway", "http://localhost:9080"),
        ("APISIX Admin", "http://localhost:9180/apisix/admin/services"),
        ("RabbitMQ Management", "http://localhost:15672"),
    ]
    
    all_good = True
    
    # Check HTTP services
    for name, url in services:
        if not check_service(name, url):
            all_good = False
    
    # Check database services
    if not check_postgres():
        all_good = False
    
    if not check_redis():
        all_good = False
    
    if not check_rabbitmq():
        all_good = False
    
    print("\n📊 Summary:")
    if all_good:
        print("✅ All services are running correctly!")
        print("\n🎯 Next steps:")
        print("   1. Test API endpoints with curl commands")
        print("   2. Monitor logs: docker-compose logs -f")
        print("   3. Check APISIX dashboard: http://localhost:9180")
    else:
        print("❌ Some services are not responding")
        print("\n🔧 Troubleshooting:")
        print("   1. Check if all containers are running: docker-compose ps")
        print("   2. View logs: docker-compose logs -f")
        print("   3. Restart services: docker-compose restart")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main()) 
#!/usr/bin/env python
import os
import time
from datetime import datetime
import logging
from pathlib import Path

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/monitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Try importing optional dependencies
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    logger.warning("psutil not installed. System resource monitoring will be disabled.")
    PSUTIL_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    logger.warning("requests not installed. HTTP health checks will be disabled.")
    REQUESTS_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    logger.warning("redis not installed. Redis monitoring will be disabled.")
    REDIS_AVAILABLE = False

def check_system_resources():
    """Monitor system resources"""
    if not PSUTIL_AVAILABLE:
        return None
    
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'disk_percent': disk.percent,
        }
    except Exception as e:
        logger.error(f"Error checking system resources: {str(e)}")
        return None

def check_application_health():
    """Check application health endpoints"""
    if not REQUESTS_AVAILABLE:
        return None
    
    try:
        response = requests.get('http://localhost:8000/health/', timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return False

def check_database_connection():
    """Check database connection"""
    try:
        import django
        from django.db import connections
        from django.db.utils import OperationalError

        db_conn = connections['default']
        db_conn.cursor()
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False

def check_redis_connection():
    """Check Redis connection"""
    if not REDIS_AVAILABLE:
        return None
        
    try:
        r = redis.Redis(
            host=os.environ.get('REDIS_HOST', 'localhost'),
            port=int(os.environ.get('REDIS_PORT', 6379)),
            password=os.environ.get('REDIS_PASSWORD', ''),
            socket_timeout=5
        )
        return r.ping()
    except Exception as e:
        logger.error(f"Redis connection check failed: {str(e)}")
        return False

def main():
    """Main monitoring loop"""
    logger.info("Starting monitoring service...")
    
    while True:
        try:
            # Check system resources
            resources = check_system_resources()
            if resources:
                logger.info(f"System resources: {resources}")

            # Check application health
            app_health = check_application_health()
            if app_health is not None:
                logger.info(f"Application health: {'OK' if app_health else 'FAIL'}")

            # Check database connection
            db_health = check_database_connection()
            logger.info(f"Database health: {'OK' if db_health else 'FAIL'}")

            # Check Redis connection
            redis_health = check_redis_connection()
            if redis_health is not None:
                logger.info(f"Redis health: {'OK' if redis_health else 'FAIL'}")

            # Alert if any checks fail
            if any(x is False for x in [app_health, db_health, redis_health]):
                logger.warning("One or more health checks failed!")
                # Implement your alerting mechanism here (email, Slack, etc.)

            # Sleep for 5 minutes
            time.sleep(300)

        except KeyboardInterrupt:
            logger.info("Monitoring service stopped by user")
            break
        except Exception as e:
            logger.error(f"Monitoring error: {str(e)}")
            time.sleep(60)  # Wait a minute before retrying

if __name__ == '__main__':
    main() 
import os
import psutil
# import redis
from django.db import connection
from django.http import JsonResponse
# from celery import current_app as celery_app
from django.core.cache import cache
from django.conf import settings


def server_health_status(request):
    health_status = {
        "database": check_database(),
        "cache": check_cache(),
        # "celery": check_celery(),
        "disk_usage": check_disk_usage(),
        "cpu_usage": check_cpu_usage(),
        "memory_usage": check_memory_usage(),
    }

    return JsonResponse(health_status)


def check_database():
    """Check if the database is reachable."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


def check_cache():
    """Check if the cache (Redis) is reachable."""
    try:
        cache.set('health_check', 'ok', timeout=5)
        if cache.get('health_check') == 'ok':
            return {"status": "healthy"}
        else:
            return {"status": "unhealthy", "error": "Cache unreachable"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# def check_celery():
    # """Check if Celery workers are running."""
    # try:
    #     celery_app.control.ping(timeout=5)
    #     return {"status": "healthy"}
    # except Exception as e:
    #     return {"status": "unhealthy", "error": str(e)}


def check_disk_usage():
    """Check disk usage."""
    disk_usage = psutil.disk_usage('/')
    return {
        "total": disk_usage.total,
        "used": disk_usage.used,
        "free": disk_usage.free,
        "percent": disk_usage.percent
    }


def check_cpu_usage():
    """Check CPU usage."""
    return {
        "percent": psutil.cpu_percent(interval=1)
    }


def check_memory_usage():
    """Check memory usage."""
    memory = psutil.virtual_memory()
    return {
        "total": memory.total,
        "available": memory.available,
        "percent": memory.percent,
        "used": memory.used,
        "free": memory.free
    }

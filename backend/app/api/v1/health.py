"""
Health check and status API endpoint.
"""
from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.config import settings
from app.core.cache import cache

router = APIRouter(prefix="/health", tags=["Système & Healthcheck"])


@router.get("", summary="État de santé de l'API et des connecteurs")
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "redis_connected": cache._redis_available,
        "cache_type": "redis" if cache._redis_available else "in_memory_ttl",
    }

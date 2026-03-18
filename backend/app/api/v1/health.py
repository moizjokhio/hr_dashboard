"""
Health check endpoints
"""

from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_async_session
from app.core.config import settings
from app.schemas.common import HealthCheck

router = APIRouter()


@router.get("/", response_model=HealthCheck)
async def health_check(
    session: AsyncSession = Depends(get_async_session)
):
    """
    Health check endpoint for load balancers and monitoring
    
    Checks:
    - API responsiveness
    - Database connectivity
    - Cache connectivity
    - Vector DB connectivity
    """
    health = HealthCheck(
        status="healthy",
        version=settings.app.APP_VERSION,
        timestamp=datetime.utcnow()
    )
    
    # Check database
    try:
        await session.execute(text("SELECT 1"))
        health.database = "connected"
    except Exception as e:
        health.database = f"error: {str(e)}"
        health.status = "degraded"
    
    # Check Redis cache
    try:
        from app.core.cache import cache_service
        if cache_service.client:
            await cache_service.client.ping()
            health.cache = "connected"
        else:
            health.cache = "not initialized"
    except Exception as e:
        health.cache = f"error: {str(e)}"
        health.status = "degraded"
    
    # Check Vector DB
    try:
        from app.ml.vector_db_service import vector_db_service
        if vector_db_service.client:
            vector_db_service.client.get_collections()
            health.vector_db = "connected"
        else:
            health.vector_db = "not initialized"
    except Exception as e:
        health.vector_db = f"error: {str(e)}"
        health.status = "degraded"
    
    return health


@router.get("/ready")
async def readiness_check():
    """
    Kubernetes readiness probe
    Returns 200 if service is ready to accept traffic
    """
    return {"ready": True}


@router.get("/live")
async def liveness_check():
    """
    Kubernetes liveness probe
    Returns 200 if service is alive
    """
    return {"alive": True}

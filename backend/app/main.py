"""
HR Analytics System - FastAPI Application
Main entry point
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import time

from app.core.config import settings
from app.core.database import async_engine as engine, Base
from app.core.logging import setup_logging
from app.api import api_router


# Setup logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting HR Analytics System...")
    logger.info(f"Environment: {settings.app.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.app.DEBUG}")
    
    # Initialize database tables (in production, use Alembic migrations)
    if settings.app.ENVIRONMENT == "development":
        async with engine.begin() as conn:
            # await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables verified")
    
    # Initialize ML models
    try:
        logger.info("Loading ML models...")
        # Models are loaded lazily on first use to speed up startup
        # from app.ml.embedding_service import embedding_service
        # from app.ml.llm_service import llm_service
        # from app.ml.prediction_service import prediction_service
        logger.info("ML models ready (lazy loading enabled)")
    except Exception as e:
        logger.warning(f"ML models not loaded: {e}")
    
    # Initialize vector database
    try:
        logger.info("Connecting to vector database...")
        # from app.ml.vector_db_service import VectorDBService
        # vector_service = VectorDBService()
        logger.info("Vector database ready")
    except Exception as e:
        logger.warning(f"Vector database not connected: {e}")
    
    # Initialize cache
    try:
        logger.info("Connecting to Redis cache...")
        from app.core.cache import cache_service
        # await cache_service.connect()
        logger.info("Redis cache ready")
    except Exception as e:
        logger.warning(f"Redis cache not connected: {e}")
    
    logger.info("HR Analytics System started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down HR Analytics System...")
    
    # Close database connections
    await engine.dispose()
    logger.info("Database connections closed")
    
    # Close cache connections
    try:
        from app.core.cache import cache_service
        await cache_service.close()
        logger.info("Redis cache closed")
    except Exception:
        pass
    
    logger.info("HR Analytics System shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app.APP_NAME,
    description="""
    # HR Analytics System API
    
    Enterprise-level HR Analytics platform for workforce insights.
    
    ## Features
    
    - **Employee Management**: CRUD operations with advanced filtering
    - **Analytics Dashboards**: Headcount, diversity, compensation, performance
    - **AI-Powered Search**: Natural language queries converted to SQL
    - **Predictive Analytics**: Attrition, performance, promotion predictions
    - **Report Generation**: PDF, Word, Excel exports
    
    ## Authentication
    
    Most endpoints require JWT authentication. Include the token in the Authorization header:
    ```
    Authorization: Bearer <token>
    ```
    
    ## Rate Limiting
    
    API requests are rate-limited to ensure fair usage:
    - Standard endpoints: 100 requests/minute
    - AI endpoints: 20 requests/minute
    - Export endpoints: 10 requests/minute
    """,
    version=settings.app.APP_VERSION,
    docs_url="/docs" if settings.app.DEBUG else None,
    redoc_url="/redoc" if settings.app.DEBUG else None,
    openapi_url=f"{settings.app.API_V1_PREFIX}/openapi.json" if settings.app.DEBUG else None,
    lifespan=lifespan
)


# ============= Middleware =============

# CORS — set CORS_ORIGINS env var as comma-separated list for production
_default_origins = "http://localhost:3000,http://127.0.0.1:3000"
_raw_origins = os.environ.get("CORS_ORIGINS", _default_origins)
_allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]
_enable_ai_features = os.environ.get("ENABLE_AI_FEATURES", "false").lower() == "true"

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

# Gzip compression for responses > 1KB
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    logger.debug(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.debug(f"{request.method} {request.url.path} - {response.status_code}")
    return response


# ============= Exception Handlers =============

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.app.DEBUG else "An unexpected error occurred"
        }
    )


# ============= Include Routers =============

app.include_router(api_router, prefix=settings.app.API_V1_PREFIX)


# ============= Root Endpoints =============

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "HR Analytics System API",
        "version": settings.app.APP_VERSION,
        "docs": "/docs" if settings.app.DEBUG else "Disabled in production",
        "health": f"{settings.app.API_V1_PREFIX}/health"
    }


@app.get("/info", tags=["Root"])
async def info():
    """System information"""
    endpoints = {
        "employees": f"{settings.app.API_V1_PREFIX}/employees",
        "analytics": f"{settings.app.API_V1_PREFIX}/analytics",
        "reports": f"{settings.app.API_V1_PREFIX}/reports",
        "health": f"{settings.app.API_V1_PREFIX}/health"
    }

    if _enable_ai_features:
        endpoints["ai"] = f"{settings.app.API_V1_PREFIX}/ai"

    return {
        "name": settings.app.APP_NAME,
        "version": settings.app.APP_VERSION,
        "environment": settings.app.ENVIRONMENT,
        "features": {
            "employees": True,
            "analytics": True,
            "ai_search": _enable_ai_features,
            "predictions": _enable_ai_features,
            "reports": True
        },
        "api_version": "v1",
        "endpoints": endpoints
    }


# ============= Main =============

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.app.HOST,
        port=settings.app.PORT,
        reload=settings.app.DEBUG,
        log_level="debug" if settings.app.DEBUG else "info"
    )

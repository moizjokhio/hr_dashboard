"""
API module initialization
"""

import os
from fastapi import APIRouter

from app.api.v1 import employees, analytics, reports, health, da_mis, upload

api_router = APIRouter()

# Include all API routers
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"]
)

api_router.include_router(
    employees.router,
    prefix="/employees",
    tags=["Employees"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics"]
)

if os.environ.get("ENABLE_AI_FEATURES", "false").lower() == "true":
    from app.api.v1 import ai

    api_router.include_router(
        ai.router,
        prefix="/ai",
        tags=["AI & Search"]
    )

api_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["Reports"]
)

api_router.include_router(
    da_mis.router,
    prefix="/da-mis",
    tags=["DA MIS Cases"]
)

api_router.include_router(
    upload.router,
    prefix="/upload",
    tags=["Data Upload"]
)

"""
API v1 module
"""
from fastapi import APIRouter

from app.api.v1 import health, employees, analytics, reports, da_mis, upload

api_router = APIRouter()

# Include all routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(employees.router, prefix="/employees", tags=["employees"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(da_mis.router, prefix="/da-mis", tags=["da-mis"])
api_router.include_router(upload.router, prefix="/upload", tags=["Data Upload"])

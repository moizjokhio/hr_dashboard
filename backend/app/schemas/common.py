"""
Common schemas for API responses
"""

from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, Field
from datetime import datetime


T = TypeVar('T')


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    error_code: Optional[str] = None
    details: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, le=1000, description="Items per page")
    total_items: int = Field(ge=0, description="Total number of items")
    total_pages: int = Field(ge=0, description="Total number of pages")
    has_next: bool = Field(description="Has next page")
    has_prev: bool = Field(description="Has previous page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper"""
    success: bool = True
    data: List[T]
    pagination: PaginationMeta
    
    class Config:
        arbitrary_types_allowed = True


class SortOrder(BaseModel):
    """Sort order specification"""
    field: str
    direction: str = Field(pattern="^(asc|desc)$", default="asc")


class QueryParams(BaseModel):
    """Common query parameters"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=1000)
    sort_by: Optional[str] = None
    sort_order: str = Field(default="asc", pattern="^(asc|desc)$")
    search: Optional[str] = None


class HealthCheck(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    database: str = "connected"
    cache: str = "connected"
    vector_db: str = "connected"


class BatchOperationResult(BaseModel):
    """Result of batch operations"""
    total: int
    successful: int
    failed: int
    errors: List[dict] = []

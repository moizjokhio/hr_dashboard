"""
Schemas module initialization
"""

from app.schemas.employee import (
    EmployeeBase,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeListResponse,
    EmployeeFilter,
    FilterBlock,
    FilterOperator,
)
from app.schemas.analytics import (
    DashboardMetrics,
    ChartDataPoint,
    AnalyticsRequest,
    AnalyticsResponse,
    PredictionRequest,
    PredictionResponse,
)
from app.schemas.ai import (
    NLPQueryRequest,
    NLPQueryResponse,
    SearchSuggestion,
    GeneratedSQL,
)
from app.schemas.common import (
    PaginatedResponse,
    ErrorResponse,
    SuccessResponse,
)

__all__ = [
    # Employee
    "EmployeeBase",
    "EmployeeCreate",
    "EmployeeUpdate",
    "EmployeeResponse",
    "EmployeeListResponse",
    "EmployeeFilter",
    "FilterBlock",
    "FilterOperator",
    # Analytics
    "DashboardMetrics",
    "ChartDataPoint",
    "AnalyticsRequest",
    "AnalyticsResponse",
    "PredictionRequest",
    "PredictionResponse",
    # AI
    "NLPQueryRequest",
    "NLPQueryResponse",
    "SearchSuggestion",
    "GeneratedSQL",
    # Common
    "PaginatedResponse",
    "ErrorResponse",
    "SuccessResponse",
]

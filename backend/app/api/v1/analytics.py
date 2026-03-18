"""
Analytics API endpoints
Dashboard metrics and visualizations
"""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.cache import cache_service
from app.services.analytics_service import AnalyticsService
from app.services.employee_service import EmployeeService
from app.schemas.analytics import (
    DashboardRequest, DashboardResponse, 
    HeadcountAnalytics, DiversityAnalytics,
    CompensationAnalytics, PerformanceAnalytics,
    AttritionAnalytics, TrendRequest
)
from app.schemas.employee import EmployeeFilter

router = APIRouter()


@router.get("/summary")
async def get_summary(
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get high-level summary metrics for dashboard header
    
    Returns:
    - Total employees
    - Active employees
    - Average salary
    - Average performance score
    - Attrition rate (30-day)
    - New hires (30-day)
    - Departments count
    - Open positions
    """
    cache_key = "analytics:summary"
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    
    service = AnalyticsService(session)
    summary = await service.get_summary_metrics()
    
    await cache_service.set(cache_key, summary, ttl=300)  # 5 min cache
    return summary


@router.get("/headcount")
async def get_headcount_analytics(
    departments: Optional[List[str]] = Query(None),
    grades: Optional[List[str]] = Query(None),
    countries: Optional[List[str]] = Query(None),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get headcount analytics with breakdown by dimensions
    
    Returns:
    - By department
    - By grade level
    - By country/region
    - By employment type
    - Year-over-year trends
    """
    filters = EmployeeFilter(
        departments=departments,
        grades=grades,
        countries=countries
    )
    
    service = AnalyticsService(session)
    analytics = await service.get_headcount_analytics(filters)
    
    return analytics


@router.get("/diversity")
async def get_diversity_analytics(
    departments: Optional[List[str]] = Query(None),
    grades: Optional[List[str]] = Query(None),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get diversity & inclusion metrics
    
    Returns:
    - Gender distribution (overall and by department/grade)
    - Age distribution
    - Education level distribution
    - Disability representation
    - Religion distribution
    - Marital status distribution
    - Diversity index scores
    """
    filters = EmployeeFilter(
        departments=departments,
        grades=grades
    )
    
    service = AnalyticsService(session)
    analytics = await service.get_diversity_analytics(filters)
    
    return analytics


@router.get("/compensation")
async def get_compensation_analytics(
    departments: Optional[List[str]] = Query(None),
    grades: Optional[List[str]] = Query(None),
    countries: Optional[List[str]] = Query(None),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get compensation analytics
    
    Returns:
    - Salary distribution (histograms)
    - Average salary by department/grade/country
    - Pay equity analysis (gender pay gap)
    - Allowances breakdown
    - Total compensation analysis
    - Salary bands and range penetration
    - Compa-ratio analysis
    """
    filters = EmployeeFilter(
        departments=departments,
        grades=grades,
        countries=countries
    )
    
    service = AnalyticsService(session)
    analytics = await service.get_compensation_analytics(filters)
    
    return analytics


@router.get("/performance")
async def get_performance_analytics(
    departments: Optional[List[str]] = Query(None),
    grades: Optional[List[str]] = Query(None),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get performance analytics
    
    Returns:
    - Performance score distribution
    - Performance by department/grade
    - High performers identification
    - Performance vs tenure analysis
    - Performance trends (YoY)
    - Top/bottom performers lists
    """
    filters = EmployeeFilter(
        departments=departments,
        grades=grades
    )
    
    service = AnalyticsService(session)
    analytics = await service.get_performance_analytics(filters)
    
    return analytics


@router.get("/attrition")
async def get_attrition_analytics(
    departments: Optional[List[str]] = Query(None),
    grades: Optional[List[str]] = Query(None),
    period_months: int = Query(12, ge=1, le=60),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get attrition and turnover analytics
    
    Returns:
    - Overall attrition rate
    - Attrition by department/grade
    - Voluntary vs involuntary
    - Attrition trends over time
    - Risk factors analysis
    - Tenure at exit analysis
    """
    filters = EmployeeFilter(
        departments=departments,
        grades=grades
    )
    
    service = AnalyticsService(session)
    analytics = await service.get_attrition_analytics(filters, period_months)
    
    return analytics


@router.get("/trends")
async def get_trends(
    metric: str = Query(..., description="Metric to trend: headcount, salary, performance, attrition"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    interval: str = Query("month", pattern="^(day|week|month|quarter|year)$"),
    departments: Optional[List[str]] = Query(None),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get time-series trends for a metric
    
    Supported metrics:
    - headcount: Employee count over time
    - salary: Average salary over time
    - performance: Average performance over time
    - attrition: Attrition rate over time
    - hires: New hires over time
    """
    allowed_metrics = ["headcount", "salary", "performance", "attrition", "hires"]
    
    if metric not in allowed_metrics:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid metric. Allowed: {allowed_metrics}"
        )
    
    filters = EmployeeFilter(departments=departments)
    
    service = AnalyticsService(session)
    trends = await service.get_metric_trends(
        metric=metric,
        filters=filters,
        start_date=start_date,
        end_date=end_date,
        interval=interval
    )
    
    return trends


@router.post("/dashboard")
async def get_custom_dashboard(
    request: DashboardRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get custom dashboard with specified metrics and filters
    
    Allows building custom dashboards with selected:
    - Metrics (which analytics modules to include)
    - Filters (applied across all metrics)
    - Breakdown dimensions
    """
    service = AnalyticsService(session)
    dashboard = await service.build_custom_dashboard(request)
    
    return dashboard


@router.get("/comparisons")
async def compare_segments(
    compare_by: str = Query(..., description="Field to compare: department, grade, country"),
    segments: List[str] = Query(..., description="Segment values to compare"),
    metrics: List[str] = Query(["headcount", "avg_salary", "avg_performance"]),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Compare metrics across segments
    
    Compare departments, grades, or regions on various metrics.
    Useful for benchmarking analysis.
    """
    allowed_fields = ["department", "grade_level", "branch_country", "employment_type"]
    
    if compare_by not in allowed_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid compare_by. Allowed: {allowed_fields}"
        )
    
    service = AnalyticsService(session)
    comparison = await service.compare_segments(
        compare_by=compare_by,
        segments=segments,
        metrics=metrics
    )
    
    return comparison


@router.get("/distribution/{field}")
async def get_distribution(
    field: str,
    departments: Optional[List[str]] = Query(None),
    grades: Optional[List[str]] = Query(None),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get distribution of employees by a specific field
    
    Returns counts for each unique value of the field.
    """
    allowed_fields = [
        "department", "grade_level", "branch_country", "branch_city",
        "gender", "employment_type", "status", "education_level",
        "marital_status", "religion", "unit_name"
    ]
    
    if field not in allowed_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid field. Allowed: {allowed_fields}"
        )
    
    filters = EmployeeFilter(
        departments=departments,
        grades=grades
    )
    
    service = EmployeeService(session)
    distribution = await service.get_distribution(field, filters)
    
    return {"field": field, "distribution": distribution}


@router.get("/salary-bands")
async def get_salary_bands(
    departments: Optional[List[str]] = Query(None),
    grades: Optional[List[str]] = Query(None),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get salary band analysis
    
    Returns:
    - Distribution within bands
    - Range penetration
    - Above/below range employees
    """
    filters = EmployeeFilter(
        departments=departments,
        grades=grades
    )
    
    service = AnalyticsService(session)
    bands = await service.get_salary_band_analysis(filters)
    
    return bands


@router.get("/workforce-planning")
async def get_workforce_planning(
    departments: Optional[List[str]] = Query(None),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get workforce planning analytics
    
    Returns:
    - Upcoming retirements
    - Succession risk
    - Skills gap analysis
    - Span of control
    - Pyramid analysis
    """
    filters = EmployeeFilter(departments=departments)
    
    service = AnalyticsService(session)
    planning = await service.get_workforce_planning(filters)
    
    return planning


@router.get("/charts/{chart_type}")
async def get_chart_data(
    chart_type: str,
    dimension: str = Query("department"),
    metric: str = Query("count"),
    limit: int = Query(10, ge=1, le=50),
    departments: Optional[List[str]] = Query(None),
    grades: Optional[List[str]] = Query(None),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get formatted chart data ready for visualization
    
    Chart types: bar, pie, line, scatter, treemap, heatmap
    Returns data in ECharts-compatible format.
    """
    allowed_charts = ["bar", "pie", "line", "scatter", "treemap", "heatmap"]
    
    if chart_type not in allowed_charts:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid chart_type. Allowed: {allowed_charts}"
        )
    
    filters = EmployeeFilter(
        departments=departments,
        grades=grades
    )
    
    service = AnalyticsService(session)
    chart_data = await service.get_chart_data(
        chart_type=chart_type,
        dimension=dimension,
        metric=metric,
        filters=filters,
        limit=limit
    )
    
    return chart_data

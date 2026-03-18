"""
Employee API endpoints
CRUD operations and advanced filtering
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import get_current_user, require_hr
from app.services.employee_service import EmployeeService
from app.schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse, 
    EmployeeFilter, EmployeeBulkCreate, EmployeeExport
)
from app.schemas.common import PaginatedResponse, SuccessResponse, ErrorResponse

router = APIRouter()


@router.get("", response_model=dict)
async def list_employees(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=1000, description="Items per page"),
    sort_by: str = Query("employee_id", description="Field to sort by"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    search: Optional[str] = Query(None, description="Search term"),
    departments: Optional[List[str]] = Query(None, description="Filter by departments"),
    grades: Optional[List[str]] = Query(None, description="Filter by grades"),
    countries: Optional[List[str]] = Query(None, description="Filter by countries"),
    statuses: Optional[List[str]] = Query(None, description="Filter by statuses"),
    salary_min: Optional[float] = Query(None, description="Minimum salary"),
    salary_max: Optional[float] = Query(None, description="Maximum salary"),
    experience_min: Optional[float] = Query(None, description="Minimum experience years"),
    experience_max: Optional[float] = Query(None, description="Maximum experience years"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    List employees with pagination and filtering
    
    Supports multiple filter parameters that can be combined.
    Returns paginated results with summary statistics.
    """
    # Build filter object from query parameters
    filters = EmployeeFilter(
        search_term=search,
        departments=departments,
        grades=grades,
        countries=countries,
        statuses=statuses,
        salary_min=salary_min,
        salary_max=salary_max,
        experience_min=experience_min,
        experience_max=experience_max
    )
    
    service = EmployeeService(session)
    result = await service.search_employees(
        filters=filters,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Convert employees to response format
    result["employees"] = [
        EmployeeResponse.model_validate(emp).model_dump()
        for emp in result["employees"]
    ]
    
    return result


@router.post("/search", response_model=dict)
async def search_employees(
    filters: EmployeeFilter,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=1000),
    sort_by: str = Query("employee_id"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Advanced employee search with stacked filter blocks
    
    Accepts complex filter configurations with multiple
    filter blocks that are combined with AND logic.
    """
    service = EmployeeService(session)
    result = await service.search_employees(
        filters=filters,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    result["employees"] = [
        EmployeeResponse.model_validate(emp).model_dump()
        for emp in result["employees"]
    ]
    
    return result


@router.get("/filters/options")
async def get_filter_options(
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get available filter options (distinct values for each field)
    
    Returns lists of unique values for:
    - Departments
    - Grades
    - Countries
    - Cities
    - Employment types
    - Statuses
    """
    service = EmployeeService(session)
    
    options = {
        "departments": await service.get_distribution("department"),
        "grades": await service.get_distribution("grade_level"),
        "countries": await service.get_distribution("branch_country"),
        "cities": await service.get_distribution("branch_city"),
        "employment_types": await service.get_distribution("employment_type"),
        "statuses": await service.get_distribution("status"),
        "religions": await service.get_distribution("religion"),
        "marital_statuses": await service.get_distribution("marital_status"),
        "education_levels": await service.get_distribution("education_level"),
        "units": await service.get_distribution("unit_name"),
    }
    
    # Convert to simple lists
    for key in options:
        options[key] = [item["value"] for item in options[key] if item["value"]]
    
    return options


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    """Get single employee by ID"""
    service = EmployeeService(session)
    employee = await service.get_employee(employee_id)
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee {employee_id} not found"
        )
    
    return EmployeeResponse.model_validate(employee)


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    data: EmployeeCreate,
    session: AsyncSession = Depends(get_async_session),
    # current_user: dict = Depends(require_hr)  # Uncomment for auth
):
    """Create new employee"""
    service = EmployeeService(session)
    
    try:
        employee = await service.create_employee(data)
        return EmployeeResponse.model_validate(employee)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: str,
    data: EmployeeUpdate,
    session: AsyncSession = Depends(get_async_session),
    # current_user: dict = Depends(require_hr)
):
    """Update employee"""
    service = EmployeeService(session)
    
    employee = await service.update_employee(employee_id, data)
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee {employee_id} not found"
        )
    
    return EmployeeResponse.model_validate(employee)


@router.delete("/{employee_id}", response_model=SuccessResponse)
async def delete_employee(
    employee_id: str,
    session: AsyncSession = Depends(get_async_session),
    # current_user: dict = Depends(require_admin)
):
    """Delete employee (soft delete - changes status to Terminated)"""
    service = EmployeeService(session)
    
    deleted = await service.delete_employee(employee_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee {employee_id} not found"
        )
    
    return SuccessResponse(message=f"Employee {employee_id} deleted")


@router.post("/bulk", response_model=dict)
async def bulk_create_employees(
    data: EmployeeBulkCreate,
    session: AsyncSession = Depends(get_async_session),
    # current_user: dict = Depends(require_admin)
):
    """
    Bulk create employees
    
    Accepts up to 10,000 employees at once.
    Returns summary of successful and failed creates.
    """
    service = EmployeeService(session)
    result = await service.bulk_create(data.employees)
    return result


@router.post("/export")
async def export_employees(
    request: EmployeeExport,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Export employees to file
    
    Supported formats: CSV, XLSX, JSON
    """
    service = EmployeeService(session)
    
    filters = request.filters or EmployeeFilter()
    
    content = await service.export_employees(
        filters=filters,
        format=request.format,
        columns=request.columns
    )
    
    # Set appropriate content type
    content_types = {
        "csv": "text/csv",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "json": "application/json"
    }
    
    filename = f"employees_export.{request.format}"
    
    return Response(
        content=content,
        media_type=content_types[request.format],
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/{employee_id}/team", response_model=dict)
async def get_employee_team(
    employee_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    """Get team analytics for a manager"""
    service = EmployeeService(session)
    
    # Verify employee exists
    employee = await service.get_employee(employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee {employee_id} not found"
        )
    
    team_stats = await service.get_team_analytics(employee_id)
    return team_stats


@router.get("/aggregations/{group_by}")
async def get_aggregations(
    group_by: str,
    departments: Optional[List[str]] = Query(None),
    grades: Optional[List[str]] = Query(None),
    statuses: Optional[List[str]] = Query(None),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get aggregated employee data grouped by dimension
    
    Available dimensions: department, grade_level, branch_country, 
    branch_city, gender, employment_type, status
    """
    allowed_dimensions = [
        "department", "grade_level", "branch_country", "branch_city",
        "gender", "employment_type", "status", "education_level",
        "marital_status", "religion", "unit_name"
    ]
    
    if group_by not in allowed_dimensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid group_by. Allowed: {allowed_dimensions}"
        )
    
    filters = EmployeeFilter(
        departments=departments,
        grades=grades,
        statuses=statuses
    )
    
    service = EmployeeService(session)
    aggregations = await service.get_aggregations(
        filters=filters,
        group_by=group_by,
        metrics=["count", "avg_salary", "avg_performance", "avg_experience"]
    )
    
    return {"data": aggregations, "group_by": group_by}

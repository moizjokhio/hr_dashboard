"""
Employee schemas for request/response validation
Comprehensive filtering system with stacking support
"""

from typing import Optional, List, Any, Union
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, validator, root_validator


class FilterOperator(str, Enum):
    """Supported filter operators"""
    EQUALS = "eq"
    NOT_EQUALS = "neq"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    BETWEEN = "between"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


class FilterCondition(BaseModel):
    """Single filter condition"""
    field: str = Field(..., description="Field name to filter on")
    operator: FilterOperator = Field(default=FilterOperator.EQUALS)
    value: Any = Field(..., description="Value to filter by")
    value_end: Optional[Any] = Field(None, description="End value for BETWEEN operator")
    
    @validator('field')
    def validate_field(cls, v):
        # Whitelist of allowed fields to prevent SQL injection
        allowed_fields = {
            'employee_id', 'first_name', 'last_name', 'email_address',
            'gender', 'date_of_birth', 'age', 'religion', 'marital_status',
            'education_level', 'department', 'unit_name', 'job_role',
            'grade_level', 'job_level_category', 'branch_country', 'branch_city',
            'branch_name', 'branch_region', 'manager_id', 'hire_date',
            'years_experience', 'employment_type', 'status', 'salary',
            'performance_score', 'attrition_risk_score', 'promotion_likelihood'
        }
        if v not in allowed_fields:
            raise ValueError(f"Invalid field: {v}. Allowed fields: {allowed_fields}")
        return v


class FilterLogic(str, Enum):
    """Logic for combining conditions within a block"""
    AND = "and"
    OR = "or"


class FilterBlock(BaseModel):
    """
    A block of filter conditions that can be combined
    Supports stacking multiple blocks for complex queries
    """
    conditions: List[FilterCondition] = Field(
        ..., 
        min_length=1,
        description="List of filter conditions in this block"
    )
    logic: FilterLogic = Field(
        default=FilterLogic.AND,
        description="How to combine conditions within this block"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "conditions": [
                    {"field": "department", "operator": "eq", "value": "Risk"},
                    {"field": "grade_level", "operator": "in", "value": ["AVP-1", "AVP-2"]}
                ],
                "logic": "and"
            }
        }


class EmployeeFilter(BaseModel):
    """
    Advanced filter system supporting multiple stacked filter blocks
    Blocks are combined with AND logic
    """
    filter_blocks: List[FilterBlock] = Field(
        default=[],
        description="List of filter blocks (combined with AND)"
    )
    
    # Quick filters (commonly used)
    departments: Optional[List[str]] = None
    grades: Optional[List[str]] = None
    countries: Optional[List[str]] = None
    cities: Optional[List[str]] = None
    statuses: Optional[List[str]] = None
    religions: Optional[List[str]] = None
    marital_statuses: Optional[List[str]] = None
    employment_types: Optional[List[str]] = None
    units: Optional[List[str]] = None
    
    # Range filters
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    age_min: Optional[int] = Field(None, ge=18)
    age_max: Optional[int] = Field(None, le=100)
    experience_min: Optional[float] = Field(None, ge=0)
    experience_max: Optional[float] = None
    performance_min: Optional[float] = Field(None, ge=0, le=5)
    performance_max: Optional[float] = Field(None, ge=0, le=5)
    
    # Date filters
    hire_date_from: Optional[date] = None
    hire_date_to: Optional[date] = None
    
    # Text search
    search_term: Optional[str] = Field(None, max_length=200)
    
    # Manager filter
    manager_id: Optional[str] = None
    include_subordinates: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "filter_blocks": [
                    {
                        "conditions": [
                            {"field": "department", "operator": "eq", "value": "Risk"}
                        ],
                        "logic": "and"
                    }
                ],
                "departments": ["Risk", "Operations"],
                "grades": ["AVP-1", "AVP-2"],
                "salary_min": 200000,
                "salary_max": 500000
            }
        }


class EmployeeBase(BaseModel):
    """Base employee schema with common fields"""
    employee_id: str = Field(..., max_length=20)
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email_address: EmailStr
    gender: str = Field(..., max_length=10)
    date_of_birth: date
    age: int = Field(..., ge=18, le=100)
    religion: Optional[str] = Field(None, max_length=50)
    marital_status: str = Field(..., max_length=30)
    education_level: str = Field(..., max_length=50)
    department: str = Field(..., max_length=100)
    unit_name: str = Field(..., max_length=100)
    job_role: str = Field(..., max_length=100)
    grade_level: str = Field(..., max_length=20)
    job_level_category: str = Field(..., max_length=50)
    branch_country: str = Field(..., max_length=100)
    branch_city: str = Field(..., max_length=100)
    branch_name: str = Field(..., max_length=200)
    branch_region: str = Field(..., max_length=100)
    manager_id: Optional[str] = Field(None, max_length=20)
    hire_date: date
    years_experience: Decimal = Field(..., ge=0)
    employment_type: str = Field(..., max_length=30)
    salary: Decimal = Field(..., ge=0)
    performance_score: Decimal = Field(..., ge=0, le=5)
    status: str = Field(..., max_length=30)


class EmployeeCreate(EmployeeBase):
    """Schema for creating new employee"""
    pass


class EmployeeUpdate(BaseModel):
    """Schema for updating employee (all fields optional)"""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email_address: Optional[EmailStr] = None
    gender: Optional[str] = Field(None, max_length=10)
    date_of_birth: Optional[date] = None
    age: Optional[int] = Field(None, ge=18, le=100)
    religion: Optional[str] = Field(None, max_length=50)
    marital_status: Optional[str] = Field(None, max_length=30)
    education_level: Optional[str] = Field(None, max_length=50)
    department: Optional[str] = Field(None, max_length=100)
    unit_name: Optional[str] = Field(None, max_length=100)
    job_role: Optional[str] = Field(None, max_length=100)
    grade_level: Optional[str] = Field(None, max_length=20)
    job_level_category: Optional[str] = Field(None, max_length=50)
    branch_country: Optional[str] = Field(None, max_length=100)
    branch_city: Optional[str] = Field(None, max_length=100)
    branch_name: Optional[str] = Field(None, max_length=200)
    branch_region: Optional[str] = Field(None, max_length=100)
    manager_id: Optional[str] = Field(None, max_length=20)
    hire_date: Optional[date] = None
    years_experience: Optional[Decimal] = Field(None, ge=0)
    employment_type: Optional[str] = Field(None, max_length=30)
    salary: Optional[Decimal] = Field(None, ge=0)
    performance_score: Optional[Decimal] = Field(None, ge=0, le=5)
    status: Optional[str] = Field(None, max_length=30)


class EmployeeResponse(EmployeeBase):
    """Schema for employee API response"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    # Predictions
    attrition_risk_score: Optional[Decimal] = None
    promotion_likelihood: Optional[Decimal] = None
    performance_prediction: Optional[Decimal] = None
    
    # Computed fields
    full_name: Optional[str] = None
    tenure_years: Optional[float] = None
    
    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    """Response schema for employee list endpoint"""
    employees: List[EmployeeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    # Aggregations
    summary: Optional[dict] = None


class EmployeeBulkCreate(BaseModel):
    """Schema for bulk employee creation"""
    employees: List[EmployeeCreate] = Field(..., min_length=1, max_length=10000)


class EmployeeExport(BaseModel):
    """Schema for employee export request"""
    format: str = Field(..., pattern="^(csv|xlsx|json)$")
    filters: Optional[EmployeeFilter] = None
    columns: Optional[List[str]] = None
    include_predictions: bool = False

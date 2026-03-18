"""
DA MIS Cases Pydantic schemas
Request/Response models for DA MIS API endpoints
"""

from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class DAMISCaseBase(BaseModel):
    """Base schema for DA MIS Case"""
    case_number: str = Field(..., description="Case #", alias="Case #")
    s_number: Optional[str] = Field(None, description="S #", alias="S #")
    emp_number: Optional[str] = Field(None, description="Emp. #", alias="Emp. #")
    name_of_staff_reported: Optional[str] = Field(None, description="Name of Staff Reported", alias="Name of Staff Reported")
    grade: Optional[str] = Field(None, description="Grade", alias="Grade")
    ft: Optional[str] = Field(None, description="FT", alias="FT")
    branch_office: Optional[str] = Field(None, description="Branch / Office", alias="Branch / Office")
    region: Optional[str] = Field(None, description="Region", alias="Region")
    cluster: Optional[str] = Field(None, description="Cluster", alias="Cluster")
    fixation_of_responsibility: Optional[str] = Field(None, description="Fixation of Responsibility", alias="Fixation of Responsibility")
    misconduct: Optional[str] = Field(None, description="Misconduct", alias="Misconduct")
    misconduct_category: Optional[str] = Field(None, description="Misconduct Category", alias="Misconduct Category")
    case_revieved: Optional[str] = Field(None, description="Case Revieved", alias="Case Revieved")
    case_received_from_audit: Optional[str] = Field(None, description="Case Received from Audit", alias="Case Received from Audit")
    charge_sheeted_date: Optional[date] = Field(None, description="Charge Sheeted Date", alias="Charge Sheeted Date")
    dac_decision: Optional[str] = Field(None, description="DAC Decision", alias="DAC Decision")
    punishment_implementation: Optional[str] = Field(None, description="Punishment Implementation", alias="Punishment Implementation")
    punishment_letter: Optional[str] = Field(None, description="Punishment Letter", alias="Punishment Letter")
    year: Optional[int] = Field(None, description="Year", alias="Year")
    quarter: Optional[str] = Field(None, description="Quarter", alias="Quarter")
    month: Optional[str] = Field(None, description="Month", alias="Month")


class DAMISCaseCreate(DAMISCaseBase):
    """Schema for creating a new DA MIS Case"""
    pass


class DAMISCaseUpdate(BaseModel):
    """Schema for updating a DA MIS Case"""
    s_number: Optional[str] = Field(None, alias="S #")
    emp_number: Optional[str] = Field(None, alias="Emp. #")
    name_of_staff_reported: Optional[str] = Field(None, alias="Name of Staff Reported")
    grade: Optional[str] = Field(None, alias="Grade")
    ft: Optional[str] = Field(None, alias="FT")
    branch_office: Optional[str] = Field(None, alias="Branch / Office")
    region: Optional[str] = Field(None, alias="Region")
    cluster: Optional[str] = Field(None, alias="Cluster")
    fixation_of_responsibility: Optional[str] = Field(None, alias="Fixation of Responsibility")
    misconduct: Optional[str] = Field(None, alias="Misconduct")
    misconduct_category: Optional[str] = Field(None, alias="Misconduct Category")
    case_revieved: Optional[str] = Field(None, alias="Case Revieved")
    case_received_from_audit: Optional[str] = Field(None, alias="Case Received from Audit")
    charge_sheeted_date: Optional[date] = Field(None, alias="Charge Sheeted Date")
    dac_decision: Optional[str] = Field(None, alias="DAC Decision")
    punishment_implementation: Optional[str] = Field(None, alias="Punishment Implementation")
    punishment_letter: Optional[str] = Field(None, alias="Punishment Letter")
    year: Optional[int] = Field(None, alias="Year")
    quarter: Optional[str] = Field(None, alias="Quarter")
    month: Optional[str] = Field(None, alias="Month")


class DAMISCaseResponse(DAMISCaseBase):
    """Schema for DA MIS Case response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class DAMISCaseList(BaseModel):
    """Schema for paginated list of DA MIS Cases"""
    total: int
    cases: List[DAMISCaseResponse]
    page: int
    page_size: int
    total_pages: int


class DAMISFilters(BaseModel):
    """Filters for DA MIS Cases"""
    year: Optional[int] = None
    quarter: Optional[str] = None
    month: Optional[str] = None
    cluster: Optional[str] = None
    region: Optional[str] = None
    branch_office: Optional[str] = None
    grade: Optional[str] = None
    misconduct_category: Optional[str] = None
    dac_decision: Optional[str] = None
    punishment_implementation: Optional[str] = None
    ft: Optional[str] = None
    search: Optional[str] = None


class PivotTableRequest(BaseModel):
    """Request schema for pivot table data"""
    rows: List[str] = Field(..., description="Row dimensions")
    columns: List[str] = Field(..., description="Column dimensions")
    values: List[str] = Field(..., description="Value metrics")
    filters: Optional[DAMISFilters] = None
    show_grand_total: bool = True


class PivotTableResponse(BaseModel):
    """Response schema for pivot table data"""
    data: List[Dict[str, Any]]
    row_headers: List[str]
    column_headers: List[str]
    grand_totals: Dict[str, Any]


class LocationHierarchyRequest(BaseModel):
    """Request for location hierarchy analysis"""
    level: str = Field(..., description="cluster, region, or branch")
    parent_filter: Optional[str] = None
    metric: str = Field(default="case_count", description="case_count or people_count")
    filters: Optional[DAMISFilters] = None


class LocationHierarchyResponse(BaseModel):
    """Response for location hierarchy analysis"""
    level: str
    data: List[Dict[str, Any]]
    total: int


class MisconductAnalysisResponse(BaseModel):
    """Response for misconduct intelligence analysis"""
    most_common_categories: List[Dict[str, Any]]
    most_severe_misconducts: List[Dict[str, Any]]
    grade_breakdown: Dict[str, Any]
    ft_breakdown: Dict[str, Any]
    repeat_vs_first_time: Dict[str, Any]


class ProcessFairnessResponse(BaseModel):
    """Response for HR process and fairness analysis"""
    lifecycle_funnel: List[Dict[str, Any]]
    sla_delays: List[Dict[str, Any]]
    pending_decisions: int
    missing_punishment_letters: int


class DashboardSummary(BaseModel):
    """Summary statistics for DA MIS dashboard"""
    total_cases: int
    total_people_involved: int
    cases_by_year: Dict[int, int]
    cases_by_cluster: Dict[str, int]
    cases_by_grade: Dict[str, int]
    top_misconduct_categories: List[Dict[str, Any]]
    pending_decisions: int
    completion_rate: float

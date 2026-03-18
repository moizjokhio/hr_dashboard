"""
DA MIS Cases API endpoints
Provides REST API for Disciplinary Action Management Information System
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case, and_, or_, distinct, cast, String
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.da_mis_case import DAMISCase
from app.schemas.da_mis import (
    DAMISCaseResponse,
    DAMISCaseList,
    DAMISFilters,
    PivotTableRequest,
    PivotTableResponse,
    LocationHierarchyRequest,
    LocationHierarchyResponse,
    MisconductAnalysisResponse,
    ProcessFairnessResponse,
    DashboardSummary
)

router = APIRouter(tags=["DA MIS Cases"])


def apply_filters(query, filters: Optional[DAMISFilters]):
    """Apply filters to query"""
    if not filters:
        return query
    
    if filters.year:
        query = query.filter(DAMISCase.year == filters.year)
    if filters.quarter:
        query = query.filter(DAMISCase.quarter == filters.quarter)
    if filters.month:
        query = query.filter(DAMISCase.month == filters.month)
    if filters.cluster:
        query = query.filter(DAMISCase.cluster == filters.cluster)
    if filters.region:
        query = query.filter(DAMISCase.region == filters.region)
    if filters.branch_office:
        query = query.filter(DAMISCase.branch_office == filters.branch_office)
    if filters.grade:
        query = query.filter(DAMISCase.grade == filters.grade)
    if filters.misconduct_category:
        query = query.filter(DAMISCase.misconduct_category == filters.misconduct_category)
    if filters.dac_decision:
        query = query.filter(DAMISCase.dac_decision == filters.dac_decision)
    if filters.punishment_implementation:
        query = query.filter(DAMISCase.punishment_implementation == filters.punishment_implementation)
    if filters.ft:
        query = query.filter(DAMISCase.ft == filters.ft)
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.filter(
            or_(
                DAMISCase.case_number.ilike(search_term),
                DAMISCase.emp_number.ilike(search_term),
                DAMISCase.name_of_staff_reported.ilike(search_term),
                DAMISCase.misconduct.ilike(search_term)
            )
        )
    
    return query


@router.get("/cases", response_model=DAMISCaseList)
def get_cases(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    year: Optional[int] = None,
    quarter: Optional[str] = None,
    month: Optional[str] = None,
    cluster: Optional[str] = None,
    region: Optional[str] = None,
    branch_office: Optional[str] = None,
    grade: Optional[str] = None,
    misconduct_category: Optional[str] = None,
    dac_decision: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get paginated list of DA MIS cases with filters"""
    
    filters = DAMISFilters(
        year=year,
        quarter=quarter,
        month=month,
        cluster=cluster,
        region=region,
        branch_office=branch_office,
        grade=grade,
        misconduct_category=misconduct_category,
        dac_decision=dac_decision,
        search=search
    )
    
    query = db.query(DAMISCase)
    query = apply_filters(query, filters)
    
    total = query.count()
    
    offset = (page - 1) * page_size
    cases = query.order_by(desc(DAMISCase.created_at)).offset(offset).limit(page_size).all()
    
    return DAMISCaseList(
        total=total,
        cases=cases,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/cases/{case_id}", response_model=DAMISCaseResponse)
def get_case_by_id(case_id: int, db: Session = Depends(get_db)):
    """Get a specific DA MIS case by ID"""
    case = db.query(DAMISCase).filter(DAMISCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.post("/pivot-table")
def get_pivot_table(request: PivotTableRequest, db: Session = Depends(get_db)):
    """
    Generate pivot table data
    Rows: DAC Decision, Punishment Implementation
    Columns: Grade
    Values: Case Count, People Count
    """
    
    query = db.query(DAMISCase)
    if request.filters:
        query = apply_filters(query, request.filters)
    
    # Build pivot data
    pivot_data = []
    
    # Get unique values for rows and columns
    row_values = {}
    for row_field in request.rows:
        field = getattr(DAMISCase, row_field.lower().replace(" ", "_"), None)
        if field:
            values = db.query(field).filter(field.isnot(None)).distinct().all()
            row_values[row_field] = [v[0] for v in values]
    
    col_values = {}
    for col_field in request.columns:
        field = getattr(DAMISCase, col_field.lower().replace(" ", "_"), None)
        if field:
            values = db.query(field).filter(field.isnot(None)).distinct().all()
            col_values[col_field] = [v[0] for v in values]
    
    # Calculate aggregates for each combination
    for row_combo in _generate_combinations(row_values):
        for col_combo in _generate_combinations(col_values):
            filters_q = query
            
            # Apply row filters
            for field, value in row_combo.items():
                db_field = getattr(DAMISCase, field.lower().replace(" ", "_"))
                filters_q = filters_q.filter(db_field == value)
            
            # Apply column filters
            for field, value in col_combo.items():
                db_field = getattr(DAMISCase, field.lower().replace(" ", "_"))
                filters_q = filters_q.filter(db_field == value)
            
            # Calculate metrics
            case_count = filters_q.count()
            people_count = filters_q.with_entities(
                func.count(distinct(DAMISCase.emp_number))
            ).scalar() or 0
            
            pivot_data.append({
                **row_combo,
                **col_combo,
                "case_count": case_count,
                "people_count": people_count
            })
    
    return {
        "data": pivot_data,
        "row_headers": list(row_values.keys()),
        "column_headers": list(col_values.keys())
    }


def _generate_combinations(values_dict):
    """Generate all combinations of values"""
    if not values_dict:
        yield {}
        return
    
    items = list(values_dict.items())
    field, values = items[0]
    rest = dict(items[1:])
    
    for value in values:
        for combo in _generate_combinations(rest):
            yield {field: value, **combo}


@router.get("/location-hierarchy", response_model=LocationHierarchyResponse)
def get_location_hierarchy(
    level: str = Query(..., regex="^(cluster|region|branch)$"),
    parent_cluster: Optional[str] = None,
    parent_region: Optional[str] = None,
    metric: str = Query("case_count", regex="^(case_count|people_count)$"),
    year: Optional[int] = None,
    quarter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get location hierarchy analysis (Cluster -> Region -> Branch)
    Cascading drill-down for problematic areas
    """
    
    query = db.query(DAMISCase)
    
    # Apply filters
    filters = DAMISFilters(year=year, quarter=quarter)
    query = apply_filters(query, filters)
    
    # Apply parent filters for drill-down
    if parent_cluster:
        query = query.filter(DAMISCase.cluster == parent_cluster)
    if parent_region:
        query = query.filter(DAMISCase.region == parent_region)
    
    # Select field based on level
    if level == "cluster":
        field = DAMISCase.cluster
    elif level == "region":
        field = DAMISCase.region
    else:  # branch
        field = DAMISCase.branch_office
    
    # Calculate metric
    if metric == "case_count":
        results = (
            query.with_entities(
                field,
                func.count(DAMISCase.id).label("count")
            )
            .filter(field.isnot(None))
            .group_by(field)
            .order_by(desc("count"))
            .all()
        )
    else:  # people_count
        results = (
            query.with_entities(
                field,
                func.count(distinct(DAMISCase.emp_number)).label("count")
            )
            .filter(field.isnot(None))
            .group_by(field)
            .order_by(desc("count"))
            .all()
        )
    
    data = [{"name": r[0], "count": r[1]} for r in results]
    total = sum(d["count"] for d in data)
    
    return LocationHierarchyResponse(
        level=level,
        data=data,
        total=total
    )


@router.get("/misconduct-analysis", response_model=MisconductAnalysisResponse)
def get_misconduct_analysis(
    year: Optional[int] = None,
    cluster: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get misconduct intelligence analysis
    - Most common misconduct categories
    - Most severe misconducts
    - Breakdowns by grade, FT status, repeat cases
    """
    
    query = db.query(DAMISCase)
    filters = DAMISFilters(year=year, cluster=cluster)
    query = apply_filters(query, filters)
    
    # Most common categories
    common_categories = (
        query.with_entities(
            DAMISCase.misconduct_category,
            func.count(DAMISCase.id).label("count")
        )
        .filter(DAMISCase.misconduct_category.isnot(None))
        .group_by(DAMISCase.misconduct_category)
        .order_by(desc("count"))
        .limit(10)
        .all()
    )
    
    # Most severe (based on punishment implementation)
    severe_misconducts = (
        query.with_entities(
            DAMISCase.misconduct,
            DAMISCase.punishment_implementation,
            func.count(DAMISCase.id).label("count")
        )
        .filter(DAMISCase.misconduct.isnot(None))
        .filter(DAMISCase.punishment_implementation.isnot(None))
        .group_by(DAMISCase.misconduct, DAMISCase.punishment_implementation)
        .order_by(desc("count"))
        .limit(10)
        .all()
    )
    
    # Grade breakdown
    grade_breakdown = (
        query.with_entities(
            DAMISCase.grade,
            func.count(DAMISCase.id).label("count")
        )
        .filter(DAMISCase.grade.isnot(None))
        .group_by(DAMISCase.grade)
        .order_by(desc("count"))
        .all()
    )
    
    # FT vs Non-FT
    ft_breakdown = (
        query.with_entities(
            DAMISCase.ft,
            func.count(DAMISCase.id).label("count")
        )
        .filter(DAMISCase.ft.isnot(None))
        .group_by(DAMISCase.ft)
        .all()
    )
    
    return MisconductAnalysisResponse(
        most_common_categories=[
            {"category": c[0], "count": c[1]} for c in common_categories
        ],
        most_severe_misconducts=[
            {"misconduct": m[0], "punishment": m[1], "count": m[2]} 
            for m in severe_misconducts
        ],
        grade_breakdown={g[0]: g[1] for g in grade_breakdown},
        ft_breakdown={ft[0]: ft[1] for ft in ft_breakdown},
        repeat_vs_first_time={}  # TODO: Implement repeat offender logic
    )


@router.get("/process-fairness", response_model=ProcessFairnessResponse)
def get_process_fairness(
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get HR process and fairness metrics
    - Lifecycle funnel
    - SLA delays
    - Pending decisions
    """
    
    query = db.query(DAMISCase)
    if year:
        query = query.filter(DAMISCase.year == year)
    
    # Lifecycle funnel counts
    total_cases = query.count()
    received_from_audit = query.filter(
        DAMISCase.case_received_from_audit.isnot(None)
    ).count()
    charge_sheeted = query.filter(
        DAMISCase.charge_sheeted_date.isnot(None)
    ).count()
    dac_decided = query.filter(
        DAMISCase.dac_decision.isnot(None)
    ).count()
    punishment_implemented = query.filter(
        DAMISCase.punishment_implementation.isnot(None)
    ).count()
    
    lifecycle_funnel = [
        {"stage": "Total Cases", "count": total_cases},
        {"stage": "Received from Audit", "count": received_from_audit},
        {"stage": "Charge Sheeted", "count": charge_sheeted},
        {"stage": "DAC Decision", "count": dac_decided},
        {"stage": "Punishment Implemented", "count": punishment_implemented},
    ]
    
    # Pending decisions
    pending = query.filter(
        or_(
            DAMISCase.dac_decision.is_(None),
            DAMISCase.dac_decision == ""
        )
    ).count()
    
    # Missing punishment letters
    missing_letters = query.filter(
        and_(
            DAMISCase.punishment_implementation.isnot(None),
            or_(
                DAMISCase.punishment_letter.is_(None),
                DAMISCase.punishment_letter == ""
            )
        )
    ).count()
    
    return ProcessFairnessResponse(
        lifecycle_funnel=lifecycle_funnel,
        sla_delays=[],  # TODO: Calculate SLA delays based on dates
        pending_decisions=pending,
        missing_punishment_letters=missing_letters
    )


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get overall dashboard summary statistics"""
    
    query = db.query(DAMISCase)
    
    total_cases = query.count()
    total_people = query.with_entities(
        func.count(distinct(DAMISCase.emp_number))
    ).scalar() or 0
    
    # Cases by year
    cases_by_year = dict(
        query.with_entities(
            DAMISCase.year,
            func.count(DAMISCase.id)
        )
        .filter(DAMISCase.year.isnot(None))
        .group_by(DAMISCase.year)
        .all()
    )
    
    # Cases by cluster
    cases_by_cluster = dict(
        query.with_entities(
            DAMISCase.cluster,
            func.count(DAMISCase.id)
        )
        .filter(DAMISCase.cluster.isnot(None))
        .group_by(DAMISCase.cluster)
        .all()
    )
    
    # Cases by grade
    cases_by_grade = dict(
        query.with_entities(
            DAMISCase.grade,
            func.count(DAMISCase.id)
        )
        .filter(DAMISCase.grade.isnot(None))
        .group_by(DAMISCase.grade)
        .all()
    )
    
    # Top misconduct categories
    top_categories = query.with_entities(
        DAMISCase.misconduct_category,
        func.count(DAMISCase.id).label("count")
    ).filter(
        DAMISCase.misconduct_category.isnot(None)
    ).group_by(
        DAMISCase.misconduct_category
    ).order_by(desc("count")).limit(5).all()
    
    # Pending decisions
    pending = query.filter(
        or_(
            DAMISCase.dac_decision.is_(None),
            DAMISCase.dac_decision == ""
        )
    ).count()
    
    # Completion rate
    completed = query.filter(
        DAMISCase.punishment_implementation.isnot(None)
    ).count()
    completion_rate = (completed / total_cases * 100) if total_cases > 0 else 0
    
    return DashboardSummary(
        total_cases=total_cases,
        total_people_involved=total_people,
        cases_by_year=cases_by_year,
        cases_by_cluster=cases_by_cluster,
        cases_by_grade=cases_by_grade,
        top_misconduct_categories=[
            {"category": c[0], "count": c[1]} for c in top_categories
        ],
        pending_decisions=pending,
        completion_rate=round(completion_rate, 2)
    )


@router.get("/filters/options")
def get_filter_options(db: Session = Depends(get_db)):
    """Get all available filter options"""
    
    return {
        "years": [y[0] for y in db.query(DAMISCase.year).filter(
            DAMISCase.year.isnot(None)
        ).distinct().order_by(desc(DAMISCase.year)).all()],
        
        "quarters": [q[0] for q in db.query(DAMISCase.quarter).filter(
            DAMISCase.quarter.isnot(None)
        ).distinct().order_by(DAMISCase.quarter).all()],
        
        "months": [m[0] for m in db.query(DAMISCase.month).filter(
            DAMISCase.month.isnot(None)
        ).distinct().all()],
        
        "clusters": [c[0] for c in db.query(DAMISCase.cluster).filter(
            DAMISCase.cluster.isnot(None)
        ).distinct().order_by(DAMISCase.cluster).all()],
        
        "regions": [r[0] for r in db.query(DAMISCase.region).filter(
            DAMISCase.region.isnot(None)
        ).distinct().order_by(DAMISCase.region).all()],
        
        "grades": [g[0] for g in db.query(DAMISCase.grade).filter(
            DAMISCase.grade.isnot(None)
        ).distinct().order_by(DAMISCase.grade).all()],
        
        "misconduct_categories": [mc[0] for mc in db.query(DAMISCase.misconduct_category).filter(
            DAMISCase.misconduct_category.isnot(None)
        ).distinct().order_by(DAMISCase.misconduct_category).all()],
        
        "dac_decisions": [d[0] for d in db.query(DAMISCase.dac_decision).filter(
            DAMISCase.dac_decision.isnot(None)
        ).distinct().order_by(DAMISCase.dac_decision).all()],
    }

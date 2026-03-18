"""
Analytics schemas for dashboard and reporting
"""

from typing import Optional, List, Dict, Any, Union
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class ChartType(str, Enum):
    """Supported chart types"""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    DONUT = "donut"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    TREEMAP = "treemap"
    SANKEY = "sankey"
    FUNNEL = "funnel"
    RADAR = "radar"
    BOXPLOT = "boxplot"
    TABLE = "table"


class MetricType(str, Enum):
    """Types of metrics for analytics"""
    COUNT = "count"
    SUM = "sum"
    AVERAGE = "average"
    MEDIAN = "median"
    PERCENTAGE = "percentage"
    RATIO = "ratio"
    TREND = "trend"
    DISTRIBUTION = "distribution"


class TimeGranularity(str, Enum):
    """Time granularity for trend analysis"""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class ChartDataPoint(BaseModel):
    """Single data point for charts"""
    label: str
    value: Union[float, int, Decimal]
    category: Optional[str] = None
    color: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChartSeries(BaseModel):
    """Data series for multi-series charts"""
    name: str
    data: List[ChartDataPoint]
    color: Optional[str] = None
    type: Optional[ChartType] = None


class ChartData(BaseModel):
    """Complete chart data structure"""
    chart_type: ChartType
    title: str
    subtitle: Optional[str] = None
    series: List[ChartSeries]
    categories: Optional[List[str]] = None
    x_axis_label: Optional[str] = None
    y_axis_label: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class DashboardMetric(BaseModel):
    """Single KPI/metric for dashboard"""
    name: str
    value: Union[float, int, str]
    previous_value: Optional[Union[float, int]] = None
    change_percentage: Optional[float] = None
    trend: Optional[str] = None  # "up", "down", "stable"
    unit: Optional[str] = None
    format: Optional[str] = None  # "number", "currency", "percentage"


class DashboardMetrics(BaseModel):
    """Collection of dashboard metrics"""
    total_employees: DashboardMetric
    active_employees: DashboardMetric
    avg_salary: DashboardMetric
    avg_tenure: DashboardMetric
    avg_performance: DashboardMetric
    attrition_rate: DashboardMetric
    diversity_ratio: DashboardMetric
    high_performers: DashboardMetric
    
    # Additional metrics
    metrics: Optional[Dict[str, DashboardMetric]] = None


class AnalyticsDimension(str, Enum):
    """Dimensions for analytics grouping"""
    DEPARTMENT = "department"
    GRADE = "grade_level"
    COUNTRY = "branch_country"
    CITY = "branch_city"
    GENDER = "gender"
    RELIGION = "religion"
    MARITAL_STATUS = "marital_status"
    EDUCATION = "education_level"
    EMPLOYMENT_TYPE = "employment_type"
    STATUS = "status"
    UNIT = "unit_name"
    JOB_ROLE = "job_role"
    AGE_GROUP = "age_group"
    TENURE_GROUP = "tenure_group"
    SALARY_BAND = "salary_band"
    PERFORMANCE_BAND = "performance_band"


class AnalyticsRequest(BaseModel):
    """Request for analytics computation"""
    metric: MetricType
    measure_field: Optional[str] = None  # Field to aggregate (e.g., "salary")
    dimension: AnalyticsDimension
    secondary_dimension: Optional[AnalyticsDimension] = None
    
    # Filters
    filters: Optional[Dict[str, Any]] = None
    
    # Time settings
    time_dimension: Optional[str] = None
    time_granularity: Optional[TimeGranularity] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    
    # Output
    chart_type: Optional[ChartType] = ChartType.BAR
    top_n: Optional[int] = Field(None, ge=1, le=100)
    include_others: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "metric": "average",
                "measure_field": "salary",
                "dimension": "department",
                "filters": {"status": ["Active"]},
                "chart_type": "bar"
            }
        }


class AnalyticsResponse(BaseModel):
    """Response from analytics computation"""
    request: AnalyticsRequest
    chart_data: ChartData
    summary: Dict[str, Any]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    cached: bool = False
    execution_time_ms: Optional[float] = None


class ComparisonRequest(BaseModel):
    """Request for comparing two employee groups"""
    group_a_filters: Dict[str, Any]
    group_b_filters: Dict[str, Any]
    group_a_name: str = "Group A"
    group_b_name: str = "Group B"
    
    compare_metrics: List[str] = [
        "headcount", "avg_salary", "avg_performance",
        "avg_tenure", "gender_ratio", "attrition_risk"
    ]
    
    include_charts: bool = True
    chart_types: Optional[List[ChartType]] = None


class ComparisonResponse(BaseModel):
    """Response from group comparison"""
    group_a: Dict[str, Any]
    group_b: Dict[str, Any]
    comparison: Dict[str, Any]
    charts: Optional[List[ChartData]] = None
    insights: Optional[List[str]] = None


class PredictionRequest(BaseModel):
    """Request for ML predictions"""
    employee_ids: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
    prediction_type: str = Field(
        ..., 
        pattern="^(attrition|performance|promotion)$"
    )
    include_shap: bool = True
    include_recommendations: bool = True
    top_features: int = Field(default=10, ge=1, le=50)


class FeatureImportance(BaseModel):
    """Feature importance from prediction"""
    feature: str
    importance: float
    direction: str  # "positive" or "negative"
    value: Any
    shap_value: Optional[float] = None


class Recommendation(BaseModel):
    """Prescriptive recommendation"""
    action: str
    impact: str  # "high", "medium", "low"
    expected_improvement: Optional[float] = None
    confidence: Optional[float] = None
    rationale: str


class PredictionResult(BaseModel):
    """Single prediction result"""
    employee_id: str
    employee_name: str
    prediction_score: float
    prediction_label: str
    confidence: float
    feature_importance: List[FeatureImportance]
    recommendations: Optional[List[Recommendation]] = None
    risk_factors: Optional[List[str]] = None


class PredictionResponse(BaseModel):
    """Response from prediction endpoint"""
    model_config = {"protected_namespaces": ()}  # Allow model_ prefix
    
    prediction_type: str
    model_version: str
    results: List[PredictionResult]
    summary: Dict[str, Any]
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class TrendAnalysis(BaseModel):
    """Trend analysis over time"""
    metric: str
    dimension: Optional[str] = None
    time_series: List[ChartDataPoint]
    trend_direction: str  # "increasing", "decreasing", "stable"
    change_rate: float
    seasonality: Optional[Dict[str, Any]] = None
    forecast: Optional[List[ChartDataPoint]] = None


class DiversityMetrics(BaseModel):
    """Diversity and inclusion metrics"""
    gender_distribution: Dict[str, float]
    religion_distribution: Dict[str, float]
    age_distribution: Dict[str, float]
    education_distribution: Dict[str, float]
    
    # Indices
    gender_diversity_index: float
    overall_diversity_score: float
    
    # By department
    department_diversity: Optional[Dict[str, Dict[str, float]]] = None
    
    # Trends
    trends: Optional[Dict[str, List[ChartDataPoint]]] = None


class DashboardRequest(BaseModel):
    """Request for custom dashboard"""
    title: str
    widgets: List[str]
    filters: Optional[Dict[str, Any]] = None


class DashboardResponse(BaseModel):
    """Response for custom dashboard"""
    title: str
    widgets: List[Any]


class HeadcountAnalytics(BaseModel):
    total: int
    by_department: Dict[str, int]
    by_grade: Dict[str, int]
    by_country: Dict[str, int]
    trends: List[ChartDataPoint]


class DiversityAnalytics(BaseModel):
    metrics: DiversityMetrics
    charts: List[ChartData]


class CompensationAnalytics(BaseModel):
    avg_salary: float
    salary_distribution: ChartData
    by_grade: Dict[str, float]


class PerformanceAnalytics(BaseModel):
    avg_score: float
    distribution: ChartData
    top_performers: List[Dict[str, Any]]


class AttritionAnalytics(BaseModel):
    rate: float
    by_department: Dict[str, float]
    risk_factors: List[str]
    predictions: List[PredictionResult]


class TrendRequest(BaseModel):
    metric: str
    start_date: date
    end_date: date
    interval: str



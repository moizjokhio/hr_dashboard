"""
AI-related schemas for NLP queries and search
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class QueryIntent(str, Enum):
    """Detected intent from NLP query"""
    FILTER = "filter"
    AGGREGATE = "aggregate"
    COMPARE = "compare"
    PREDICT = "predict"
    TREND = "trend"
    REPORT = "report"
    SEARCH = "search"
    UNKNOWN = "unknown"


class EntityType(str, Enum):
    """Recognized entity types in queries"""
    DEPARTMENT = "department"
    GRADE = "grade"
    LOCATION = "location"
    DATE = "date"
    NUMBER = "number"
    PERCENTAGE = "percentage"
    METRIC = "metric"
    COMPARISON = "comparison"
    TIME_PERIOD = "time_period"


class ExtractedEntity(BaseModel):
    """Entity extracted from NLP query"""
    entity_type: EntityType
    value: Any
    original_text: str
    start_pos: int
    end_pos: int
    confidence: float


class NLPQueryRequest(BaseModel):
    """Request for NLP query processing"""
    query: str = Field(..., min_length=3, max_length=1000)
    context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    
    # Preferences
    preferred_chart_type: Optional[str] = None
    include_predictions: bool = True
    include_recommendations: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Compare AVP-1 employees in Risk vs Operations with >10 years experience. Show salary differences and attrition predictions."
            }
        }


class GeneratedSQL(BaseModel):
    """SQL generated from NLP query"""
    raw_sql: str
    parameterized_sql: str
    parameters: Dict[str, Any]
    tables_used: List[str]
    estimated_rows: Optional[int] = None
    execution_plan: Optional[str] = None


class QueryInterpretation(BaseModel):
    """How the AI interpreted the query"""
    original_query: str
    cleaned_query: str
    detected_intent: QueryIntent
    entities: List[ExtractedEntity]
    filters: Dict[str, Any]
    aggregations: List[str]
    comparisons: Optional[List[Dict[str, Any]]] = None
    time_range: Optional[Dict[str, str]] = None
    confidence: float


class ChartRecommendation(BaseModel):
    """Recommended chart for the query"""
    chart_type: str
    reason: str
    config: Dict[str, Any]
    priority: int = 1


class NLPQueryResponse(BaseModel):
    """Response from NLP query processing"""
    success: bool
    interpretation: QueryInterpretation
    generated_sql: GeneratedSQL
    
    # Results
    data: Optional[List[Dict[str, Any]]] = None
    row_count: int = 0
    
    # Visualizations
    chart_recommendations: List[ChartRecommendation]
    chart_data: Optional[Dict[str, Any]] = None
    # Frontend convenience fields
    results: Optional[List[Dict[str, Any]]] = None
    visualizations: Optional[List[Dict[str, Any]]] = None
    analysis: Optional[str] = None
    
    # Additional insights
    insights: Optional[List[str]] = None
    follow_up_questions: Optional[List[str]] = None
    
    # Metadata
    processing_time_ms: float
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # For complex queries
    sub_queries: Optional[List["NLPQueryResponse"]] = None


class SearchSuggestion(BaseModel):
    """Autocomplete/search suggestion"""
    text: str
    category: str
    score: float
    metadata: Optional[Dict[str, Any]] = None
    
    # For semantic search
    embedding_match: bool = False
    similar_queries: Optional[List[str]] = None


class SearchSuggestionsResponse(BaseModel):
    """Response with search suggestions"""
    query: str
    suggestions: List[SearchSuggestion]
    semantic_suggestions: Optional[List[SearchSuggestion]] = None


class ConversationMessage(BaseModel):
    """Single message in AI conversation"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None


class ConversationContext(BaseModel):
    """Context for multi-turn conversations"""
    session_id: str
    messages: List[ConversationMessage]
    current_filters: Optional[Dict[str, Any]] = None
    current_results: Optional[Dict[str, Any]] = None
    user_preferences: Optional[Dict[str, Any]] = None


class AIAnalysisRequest(BaseModel):
    """Request for complex AI analysis"""
    query: str
    analysis_type: str = Field(
        default="comprehensive",
        pattern="^(comprehensive|comparison|prediction|trend)$"
    )
    
    # What to include
    include_salary_analysis: bool = True
    include_diversity_analysis: bool = True
    include_performance_analysis: bool = True
    include_attrition_predictions: bool = True
    include_recommendations: bool = True
    
    # Output preferences
    output_format: str = Field(default="json", pattern="^(json|pdf|docx|xlsx)$")
    chart_types: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Compare AVP-1 employees in Risk vs Operations with >10 years experience. Show salary differences, diversity, performance, and attrition predictions.",
                "analysis_type": "comparison",
                "output_format": "json"
            }
        }


class AIAnalysisResponse(BaseModel):
    """Response from complex AI analysis"""
    query: str
    analysis_type: str
    
    # Structured analysis sections
    summary: str
    key_findings: List[str]
    
    # Detailed sections
    salary_analysis: Optional[Dict[str, Any]] = None
    diversity_analysis: Optional[Dict[str, Any]] = None
    performance_analysis: Optional[Dict[str, Any]] = None
    attrition_analysis: Optional[Dict[str, Any]] = None
    
    # Charts
    charts: List[Dict[str, Any]] = []
    
    # Recommendations
    recommendations: List[Dict[str, Any]] = []
    
    # Export options
    export_available: List[str] = ["pdf", "docx", "xlsx"]
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: float


class AISearchRequest(BaseModel):
    query: str
    limit: int = 10
    filters: Optional[Dict[str, Any]] = None


class AISearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total: int


class PredictionRequest(BaseModel):
    employee_ids: List[str]
    prediction_type: Optional[str] = None
    include_explanations: bool = True


class PredictionResponse(BaseModel):
    predictions: List[Dict[str, Any]]


class BatchPredictionRequest(BaseModel):
    employee_ids: List[str]
    prediction_type: Optional[str] = None
    include_explanations: bool = True
    prediction_types: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
    employee_count: Optional[int] = None


class ModelInfoResponse(BaseModel):
    name: str
    version: str
    accuracy: float


class AnalysisGenerationRequest(BaseModel):
    data: Dict[str, Any]
    analysis_type: str = Field(
        default="executive_summary",
        pattern="^(executive_summary|detailed_analysis|recommendations|comparison)$"
    )
    focus_areas: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None


class SHAPExplanationResponse(BaseModel):
    features: List[str]
    values: List[float]


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_id: Optional[str] = None


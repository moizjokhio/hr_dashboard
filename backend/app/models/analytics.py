"""
Analytics and reporting models
Store precomputed analytics, predictions, and user queries
"""

from datetime import datetime, date
from typing import Optional, List
import uuid
import enum

from sqlalchemy import (
    Column, String, Integer, DateTime, Date, Text,
    ForeignKey, Enum, Index, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.database import Base


class SnapshotType(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class PredictionType(str, enum.Enum):
    ATTRITION = "attrition"
    PERFORMANCE = "performance"
    PROMOTION = "promotion"
    SALARY = "salary"


class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalyticsSnapshot(Base):
    """
    Pre-computed analytics snapshots for fast dashboard loading
    Stores aggregated metrics by different dimensions
    """
    
    __tablename__ = "analytics_snapshots"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    # Snapshot identification
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    snapshot_type: Mapped[str] = mapped_column(String(20), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Dimension (what this metric is grouped by)
    dimension: Mapped[str] = mapped_column(String(50), nullable=False)
    dimension_value: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # Metric values
    metric_value: Mapped[float] = mapped_column(nullable=False)
    metric_count: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Additional breakdowns stored as JSON
    breakdown: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    __table_args__ = (
        Index('ix_snapshot_date_metric', 'snapshot_date', 'metric_name'),
        Index('ix_snapshot_dim', 'dimension', 'dimension_value'),
    )
    
    def __repr__(self):
        return f"<AnalyticsSnapshot {self.metric_name}: {self.dimension_value}>"


class PredictionResult(Base):
    """
    Store ML model predictions for employees
    Enables tracking prediction history and model performance
    """
    
    __tablename__ = "prediction_results"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    # Employee reference
    employee_id: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("employees.employee_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Prediction details
    prediction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    prediction_score: Mapped[float] = mapped_column(nullable=False)
    prediction_label: Mapped[Optional[str]] = mapped_column(String(50))
    confidence: Mapped[Optional[float]] = mapped_column()
    
    # Feature importance / SHAP values
    feature_importance: Mapped[Optional[dict]] = mapped_column(JSONB)
    shap_values: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Prescriptive recommendations
    recommendations: Mapped[Optional[List[dict]]] = mapped_column(JSONB)
    
    # Model input features (for reproducibility)
    input_features: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Timestamps
    prediction_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Actual outcome (for model validation)
    actual_outcome: Mapped[Optional[str]] = mapped_column(String(100))
    outcome_date: Mapped[Optional[date]] = mapped_column(Date)
    
    __table_args__ = (
        Index('ix_pred_emp_type', 'employee_id', 'prediction_type'),
        Index('ix_pred_date', 'prediction_date', 'prediction_type'),
    )
    
    def __repr__(self):
        return f"<Prediction {self.prediction_type} for {self.employee_id}>"


class AuditLog(Base):
    """
    Comprehensive audit logging for compliance
    Track all data access and modifications
    """
    
    __tablename__ = "audit_logs"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    # Action details
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(100))
    
    # User performing action
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    username: Mapped[Optional[str]] = mapped_column(String(100))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Request details
    request_method: Mapped[Optional[str]] = mapped_column(String(10))
    request_path: Mapped[Optional[str]] = mapped_column(String(500))
    request_body: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Changes made
    changes: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Result
    status_code: Mapped[Optional[int]] = mapped_column(Integer)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        index=True
    )
    
    __table_args__ = (
        Index('ix_audit_user_date', 'user_id', 'created_at'),
        Index('ix_audit_resource', 'resource_type', 'resource_id'),
    )
    
    def __repr__(self):
        return f"<AuditLog {self.action} on {self.resource_type}>"


class SavedQuery(Base):
    """
    Store user-saved queries and filters
    Enables reusable analytics and scheduled reports
    """
    
    __tablename__ = "saved_queries"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    # Owner
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Query details
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # The actual query
    query_type: Mapped[str] = mapped_column(String(50), nullable=False)  # filter, nlp, sql
    query_text: Mapped[Optional[str]] = mapped_column(Text)  # Original NLP query
    generated_sql: Mapped[Optional[str]] = mapped_column(Text)  # Generated SQL
    filters: Mapped[Optional[dict]] = mapped_column(JSONB)  # Structured filters
    
    # Visualization preferences
    chart_config: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Sharing
    is_public: Mapped[bool] = mapped_column(default=False)
    shared_with: Mapped[Optional[List[str]]] = mapped_column(ARRAY(UUID(as_uuid=True)))
    
    # Scheduling
    is_scheduled: Mapped[bool] = mapped_column(default=False)
    schedule_cron: Mapped[Optional[str]] = mapped_column(String(100))
    last_run: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now()
    )
    
    def __repr__(self):
        return f"<SavedQuery {self.name}>"


class Report(Base):
    """
    Generated reports (PDF, Word, Excel)
    Track report generation status and storage
    """
    
    __tablename__ = "reports"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    # Owner
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True
    )
    
    # Report details
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)  # pdf, docx, xlsx
    
    # Status
    status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False,
        default="pending"
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Source query/filters
    source_query_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    filters: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Generated file
    file_path: Mapped[Optional[str]] = mapped_column(String(500))
    file_size: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    __table_args__ = (
        Index('ix_report_user_status', 'user_id', 'status'),
    )
    
    def __repr__(self):
        return f"<Report {self.name} ({self.status})>"

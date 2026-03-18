"""
Employee database models
Comprehensive employee data structure for HR analytics
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
import uuid

from sqlalchemy import (
    Column, String, Integer, Date, DateTime, Numeric, 
    ForeignKey, Text, Boolean, Enum, Index, CheckConstraint,
    func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, Mapped, mapped_column
import enum

from app.core.database import Base


class Gender(str, enum.Enum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"


class EmploymentType(str, enum.Enum):
    FULL_TIME = "Full-Time"
    PART_TIME = "Part-Time"
    CONTRACT = "Contract"
    SECONDMENT = "Secondment"


class EmploymentStatus(str, enum.Enum):
    ACTIVE = "Active"
    RESIGNED = "Resigned"
    SUSPENDED = "Suspended"
    ON_LEAVE = "On-Leave"
    TERMINATED = "Terminated"
    RETIRED = "Retired"


class MaritalStatus(str, enum.Enum):
    NEVER_MARRIED = "Never Married"
    MARRIED = "Married"
    WIDOWED = "Widowed"
    DIVORCED = "Divorced"
    SEPARATED = "Separated"


class Employee(Base):
    """
    Core employee model representing all employee data
    
    Indexes optimized for common query patterns:
    - Department + Grade filtering
    - Location-based queries
    - Status and date range queries
    """
    
    __tablename__ = "employees"
    
    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    # Employee identifier (business key)
    employee_id: Mapped[str] = mapped_column(
        String(20), 
        unique=True, 
        nullable=False,
        index=True
    )
    
    # Personal Information
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email_address: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        nullable=False
    )
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Demographics
    religion: Mapped[Optional[str]] = mapped_column(String(50))
    marital_status: Mapped[str] = mapped_column(String(30), nullable=False)
    nationality: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Education
    education_level: Mapped[str] = mapped_column(String(50), nullable=False)
    education_institution: Mapped[Optional[str]] = mapped_column(String(200))
    education_major: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Organizational Structure
    department: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    unit_name: Mapped[str] = mapped_column(String(100), nullable=False)
    job_role: Mapped[str] = mapped_column(String(100), nullable=False)
    grade_level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    job_level_category: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Location
    branch_country: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    branch_city: Mapped[str] = mapped_column(String(100), nullable=False)
    branch_name: Mapped[str] = mapped_column(String(200), nullable=False)
    branch_region: Mapped[str] = mapped_column(String(100), nullable=False)
    branch_code: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Reporting Structure
    manager_id: Mapped[Optional[str]] = mapped_column(
        String(20), 
        ForeignKey("employees.employee_id", ondelete="SET NULL")
    )
    
    # Employment Details
    hire_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    years_experience: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    employment_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    termination_date: Mapped[Optional[date]] = mapped_column(Date)
    termination_reason: Mapped[Optional[str]] = mapped_column(String(200))
    
    # Compensation
    salary: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="PKR")
    salary_grade: Mapped[Optional[str]] = mapped_column(String(20))
    last_salary_review: Mapped[Optional[date]] = mapped_column(Date)
    bonus_eligible: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Performance
    performance_score: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)
    last_performance_review: Mapped[Optional[date]] = mapped_column(Date)
    performance_rating: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Predictions (updated by ML models)
    attrition_risk_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    promotion_likelihood: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    performance_prediction: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2))
    
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
    
    # Extended attributes (flexible JSON storage)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(
        "metadata", JSONB, default=dict
    )
    skills: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String(100)))
    certifications: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String(200)))
    
    # Relationships
    manager = relationship(
        "Employee", 
        remote_side=[employee_id],
        backref="direct_reports"
    )
    history = relationship(
        "EmployeeHistory", 
        back_populates="employee",
        cascade="all, delete-orphan"
    )
    
    # Indexes for common query patterns
    __table_args__ = (
        # Composite indexes for filtered queries
        Index('ix_emp_dept_grade', 'department', 'grade_level'),
        Index('ix_emp_country_city', 'branch_country', 'branch_city'),
        Index('ix_emp_status_date', 'status', 'hire_date'),
        Index('ix_emp_dept_status', 'department', 'status'),
        Index('ix_emp_grade_salary', 'grade_level', 'salary'),
        
        # Check constraints
        CheckConstraint('age >= 18 AND age <= 100', name='check_age_range'),
        CheckConstraint('salary >= 0', name='check_positive_salary'),
        CheckConstraint(
            'performance_score >= 0 AND performance_score <= 5', 
            name='check_performance_range'
        ),
    )
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @property
    def tenure_years(self) -> float:
        """Calculate tenure from hire date"""
        today = date.today()
        delta = today - self.hire_date
        return round(delta.days / 365.25, 2)
    
    def __repr__(self):
        return f"<Employee {self.employee_id}: {self.full_name}>"


class EmployeeHistory(Base):
    """
    Track historical changes to employee records for auditing
    and time-series analysis
    """
    
    __tablename__ = "employee_history"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    employee_id: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("employees.employee_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Change tracking
    change_type: Mapped[str] = mapped_column(String(50), nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[Optional[str]] = mapped_column(Text)
    new_value: Mapped[Optional[str]] = mapped_column(Text)
    
    # Context
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(500))
    changed_by: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Snapshot of employee state at change time
    snapshot: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Relationships
    employee = relationship("Employee", back_populates="history")
    
    __table_args__ = (
        Index('ix_emp_hist_date', 'employee_id', 'effective_date'),
        Index('ix_emp_hist_type', 'change_type', 'created_at'),
    )
    
    def __repr__(self):
        return f"<EmployeeHistory {self.employee_id}: {self.change_type}>"

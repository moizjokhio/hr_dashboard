"""
DA MIS Cases database model
Disciplinary Action Management Information System cases
"""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Column, String, Integer, Date, DateTime, Text, Index, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DAMISCase(Base):
    """
    DA MIS Cases - Disciplinary Action Management Information System
    Stores comprehensive data about disciplinary cases across the organization
    """
    __tablename__ = "da_mis_cases"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Case identifiers - EXACT column names as required
    case_number: Mapped[str] = mapped_column(
        "case_number", String(100), nullable=False, index=True, 
        comment="Case #"
    )
    s_number: Mapped[Optional[str]] = mapped_column(
        "s_number", String(100), nullable=True, 
        comment="S #"
    )
    emp_number: Mapped[Optional[str]] = mapped_column(
        "emp_number", String(100), nullable=True, index=True, 
        comment="Emp. #"
    )
    
    # Staff information
    name_of_staff_reported: Mapped[Optional[str]] = mapped_column(
        "name_of_staff_reported", Text, nullable=True, 
        comment="Name of Staff Reported"
    )
    grade: Mapped[Optional[str]] = mapped_column(
        "grade", String(50), nullable=True, 
        comment="Grade"
    )
    ft: Mapped[Optional[str]] = mapped_column(
        "ft", String(50), nullable=True, 
        comment="FT"
    )
    
    # Location information
    branch_office: Mapped[Optional[str]] = mapped_column(
        "branch_office", String(200), nullable=True, 
        comment="Branch / Office"
    )
    region: Mapped[Optional[str]] = mapped_column(
        "region", String(100), nullable=True, 
        comment="Region"
    )
    cluster: Mapped[Optional[str]] = mapped_column(
        "cluster", String(100), nullable=True, 
        comment="Cluster"
    )
    
    # Case details
    fixation_of_responsibility: Mapped[Optional[str]] = mapped_column(
        "fixation_of_responsibility", Text, nullable=True, 
        comment="Fixation of Responsibility"
    )
    misconduct: Mapped[Optional[str]] = mapped_column(
        "misconduct", Text, nullable=True, 
        comment="Misconduct"
    )
    misconduct_category: Mapped[Optional[str]] = mapped_column(
        "misconduct_category", String(200), nullable=True, 
        comment="Misconduct Category"
    )
    
    # Case processing
    case_revieved: Mapped[Optional[str]] = mapped_column(
        "case_revieved", String(200), nullable=True, 
        comment="Case Revieved"
    )
    case_received_from_audit: Mapped[Optional[str]] = mapped_column(
        "case_received_from_audit", String(200), nullable=True, 
        comment="Case Received from Audit"
    )
    charge_sheeted_date: Mapped[Optional[date]] = mapped_column(
        "charge_sheeted_date", Date, nullable=True, 
        comment="Charge Sheeted Date"
    )
    
    # Decision and punishment
    dac_decision: Mapped[Optional[str]] = mapped_column(
        "dac_decision", String(200), nullable=True, 
        comment="DAC Decision"
    )
    punishment_implementation: Mapped[Optional[str]] = mapped_column(
        "punishment_implementation", String(200), nullable=True, 
        comment="Punishment Implementation"
    )
    punishment_letter: Mapped[Optional[str]] = mapped_column(
        "punishment_letter", String(200), nullable=True, 
        comment="Punishment Letter"
    )
    
    # Time period
    year: Mapped[Optional[int]] = mapped_column(
        "year", Integer, nullable=True, 
        comment="Year"
    )
    quarter: Mapped[Optional[str]] = mapped_column(
        "quarter", String(10), nullable=True, 
        comment="Quarter"
    )
    month: Mapped[Optional[str]] = mapped_column(
        "month", String(20), nullable=True, 
        comment="Month"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<DAMISCase(case_number='{self.case_number}', emp_number='{self.emp_number}')>"

    def to_dict(self) -> dict:
        """Convert model to dictionary with original column names"""
        return {
            "id": self.id,
            "Case #": self.case_number,
            "S #": self.s_number,
            "Emp. #": self.emp_number,
            "Name of Staff Reported": self.name_of_staff_reported,
            "Grade": self.grade,
            "FT": self.ft,
            "Branch / Office": self.branch_office,
            "Region": self.region,
            "Cluster": self.cluster,
            "Fixation of Responsibility": self.fixation_of_responsibility,
            "Misconduct": self.misconduct,
            "Misconduct Category": self.misconduct_category,
            "Case Revieved": self.case_revieved,
            "Case Received from Audit": self.case_received_from_audit,
            "Charge Sheeted Date": self.charge_sheeted_date.isoformat() if self.charge_sheeted_date else None,
            "DAC Decision": self.dac_decision,
            "Punishment Implementation": self.punishment_implementation,
            "Punishment Letter": self.punishment_letter,
            "Year": self.year,
            "Quarter": self.quarter,
            "Month": self.month,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Add indexes for better query performance
__table_args__ = (
    Index('idx_da_mis_cases_year', 'year'),
    Index('idx_da_mis_cases_cluster', 'cluster'),
    Index('idx_da_mis_cases_region', 'region'),
    Index('idx_da_mis_cases_grade', 'grade'),
    Index('idx_da_mis_cases_misconduct_category', 'misconduct_category'),
    Index('idx_da_mis_cases_dac_decision', 'dac_decision'),
)

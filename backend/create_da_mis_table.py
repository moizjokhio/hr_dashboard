"""Manually create DA MIS table"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.db.SYNC_DATABASE_URL)

# SQL to create table
create_sql = """
CREATE TABLE IF NOT EXISTS da_mis_cases (
    id SERIAL PRIMARY KEY,
    case_number VARCHAR(100) NOT NULL,
    s_number VARCHAR(100),
    emp_number VARCHAR(100),
    name_of_staff_reported TEXT,
    grade VARCHAR(50),
    ft VARCHAR(50),
    branch_office VARCHAR(200),
    region VARCHAR(100),
    cluster VARCHAR(100),
    fixation_of_responsibility TEXT,
    misconduct TEXT,
    misconduct_category VARCHAR(200),
    case_revieved VARCHAR(200),
    case_received_from_audit VARCHAR(200),
    charge_sheeted_date DATE,
    dac_decision VARCHAR(200),
    punishment_implementation VARCHAR(200),
    punishment_letter VARCHAR(200),
    year INTEGER,
    quarter VARCHAR(10),
    month VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_da_mis_cases_case_number ON da_mis_cases(case_number);
CREATE INDEX IF NOT EXISTS idx_da_mis_cases_emp_number ON da_mis_cases(emp_number);
CREATE INDEX IF NOT EXISTS idx_da_mis_cases_year ON da_mis_cases(year);
CREATE INDEX IF NOT EXISTS idx_da_mis_cases_cluster ON da_mis_cases(cluster);
CREATE INDEX IF NOT EXISTS idx_da_mis_cases_region ON da_mis_cases(region);
CREATE INDEX IF NOT EXISTS idx_da_mis_cases_grade ON da_mis_cases(grade);
CREATE INDEX IF NOT EXISTS idx_da_mis_cases_misconduct_category ON da_mis_cases(misconduct_category);
CREATE INDEX IF NOT EXISTS idx_da_mis_cases_dac_decision ON da_mis_cases(dac_decision);
"""

with engine.connect() as conn:
    conn.execute(text(create_sql))
    conn.commit()
    print("DA MIS Cases table created successfully!")

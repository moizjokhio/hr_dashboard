#!/usr/bin/env python3
"""
Standalone ODBC Data Seeder
============================
This script seeds ODBC data from an Excel file into the PostgreSQL database.
It can be run from any computer with Python installed.

Usage:
    python seed_odbc_standalone.py "C:\path\to\your\file.xlsx"

Requirements:
    pip install pandas openpyxl sqlalchemy psycopg2-binary

Author: HR Analytics System
"""

import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "hr_admin"
DB_PASSWORD = "zbfXZpBPyxgEYEVm"
DB_NAME = "hr_analytics"

# ============================================================================
# ODBC TABLE COLUMNS (Do not modify)
# ============================================================================
ODBC_COLUMNS = [
    "EMPLOYEE_NUMBER", "ASSIGNMENT_NUMBER", "TITLE", "EMPLOYEE_FULL_NAME", 
    "GENDER", "DATE_OF_BIRTH", "FATHER_NAME", "NATIONALITY", "CNIC_NATIONAL_ID", 
    "DATE_OF_JOIN", "PHONE_TYPE", "CONTACT_NUMBER", "EMAIL_TYPE", "EMAIL_ADDRESS", 
    "ADDRESS_TYPE", "HOME_ADDRESS", "BLOOD_GROUP", "RELIGION", "ACTION_CODE", 
    "ASSIGNMENT_START_DATE", "ASSIGNMENT_END_DATE", "ASSIGNMENT_CATEGORY", 
    "DATE_PROBATION_END", "PROBATION_DURATION", "CONFIRMED_DATE", "DEPARTMENT_NAME", 
    "DEPARTMENT_TYPE", "POSITION_CODE", "POSITION_NAME", "CADRE", "GRADE", 
    "LOCATION_NAME", "JOB_NAME", "CONTRACT_TYPE", "DEPT_GROUP", "SUB_GROUP", 
    "DIVISION", "CLUSTERS", "REGION", "DISTRICT", "BRANCH", "BRANCH_LEVEL", 
    "BRANCH_FLAGSHIP", "EMPLOYMENT_STATUS", "MANAGER_EMP_NAME", "MANAGER_EMP_NO", 
    "DATE_OF_DEATH", "MARITAL_STATUS", "LAST_WORKING_DATE", "ACTUAL_TERMINATION_DATE", 
    "ACTION_REASON", "NOTIFIED_TERMINATION_DATE", "PROJECTED_TERMINATION_DATE", 
    "NOTICE_PERIOD", "GROSS_SALARY", "FESTIVAL_FLAG", "GRATUITY", "SPI_FLAG", 
    "PF_CONVERTED", "PF_CON_DATE", "PF", "PF_AMEEN", "GPF", "PENSION", "COMP_ABS", 
    "POST_RET_MED", "BF", "REL_ALL", "UNION_MEM", "EXTG_FUEL_ENTIT_OR_BMC", 
    "CANCEL_WORKRELSHIP_FLAG", "CANCEL_WORK_RELATIONSHIP_DATE", "CONTRACT_END_DATE", 
    "PERSON_TYPE", "CRC", "EXPENSE_POP", "LEAVE_FLAG", "SEQ"
]

# ============================================================================
# FUNCTIONS
# ============================================================================

def validate_file(file_path: str) -> Path:
    """Validate the Excel file exists and has correct extension."""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if path.suffix.lower() not in ['.xlsx', '.xls']:
        raise ValueError(f"File must be an Excel file (.xlsx or .xls), got: {path.suffix}")
    
    return path


def load_excel_data(file_path: Path) -> pd.DataFrame:
    """Load Excel file and normalize column names."""
    print(f"📂 Loading Excel file: {file_path.name}")
    
    try:
        # Read Excel file
        df = pd.read_excel(file_path, dtype=str)
        print(f"✓ Loaded {len(df)} rows from Excel")
        
        # Normalize column names to uppercase and strip whitespace
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Keep only valid ODBC columns
        valid_cols = set(ODBC_COLUMNS)
        original_cols = set(df.columns)
        df = df[[c for c in df.columns if c in valid_cols]]
        
        # Report on columns
        matched_cols = original_cols.intersection(valid_cols)
        ignored_cols = original_cols - valid_cols
        
        print(f"✓ Matched {len(matched_cols)} columns")
        if ignored_cols:
            print(f"⚠ Ignored {len(ignored_cols)} unknown columns: {', '.join(list(ignored_cols)[:5])}{'...' if len(ignored_cols) > 5 else ''}")
        
        if df.empty or len(df.columns) == 0:
            raise ValueError("No valid ODBC columns found in the Excel file")
        
        return df
        
    except Exception as e:
        raise Exception(f"Failed to load Excel file: {str(e)}")


def get_database_engine():
    """Create database connection engine."""
    connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    try:
        engine = create_engine(connection_string)
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"✓ Connected to database: {DB_NAME}")
        return engine
    except Exception as e:
        raise Exception(f"Failed to connect to database: {str(e)}")


def seed_odbc_table(df: pd.DataFrame, engine):
    """Truncate ODBC table and insert new data."""
    try:
        with engine.begin() as conn:
            # Truncate table
            print("🗑 Truncating ODBC table...")
            conn.execute(text("TRUNCATE TABLE odbc"))
            
            # Insert data
            print(f"📥 Inserting {len(df)} rows...")
            df.to_sql("odbc", con=conn, if_exists="append", index=False, method="multi")
            
        print(f"✅ Successfully inserted {len(df)} rows into ODBC table")
        
    except Exception as e:
        raise Exception(f"Failed to seed ODBC table: {str(e)}")


def main():
    """Main execution function."""
    print("=" * 70)
    print("ODBC DATA SEEDER")
    print("=" * 70)
    
    # Check if file path provided
    if len(sys.argv) < 2:
        print("\n❌ Error: No file path provided")
        print("\nUsage:")
        print('    python seed_odbc_standalone.py "C:\\path\\to\\your\\file.xlsx"')
        print("\nExample:")
        print('    python seed_odbc_standalone.py "C:\\Users\\John\\Desktop\\odbc_data.xlsx"')
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        # Step 1: Validate file
        print("\n[1/4] Validating file...")
        validated_path = validate_file(file_path)
        
        # Step 2: Load Excel data
        print("\n[2/4] Loading Excel data...")
        df = load_excel_data(validated_path)
        
        # Step 3: Connect to database
        print("\n[3/4] Connecting to database...")
        engine = get_database_engine()
        
        # Step 4: Seed data
        print("\n[4/4] Seeding ODBC table...")
        seed_odbc_table(df, engine)
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS! ODBC data has been seeded successfully!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\n" + "=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()

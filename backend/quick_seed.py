#!/usr/bin/env python3
"""
Standalone ODBC Data Seeder - Direct Seed
===========================================
Seeds ODBC data directly from the sample file.

Usage:
    python quick_seed.py

Requirements:
    pip install pandas openpyxl pyxlsb sqlalchemy psycopg2-binary
"""

import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
import logging

# Disable ALL verbose SQLAlchemy logging
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.pool').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.dialects').setLevel(logging.ERROR)

# ============================================================================
# CONFIGURATION
# ============================================================================
SEED_FOLDER = Path(r"C:\Users\dell\Employee_Tracker\hr-analytics-system\Seed_data")
SEED_FILE_XLSX = SEED_FOLDER / "ODBC_sample.xlsx"
SEED_FILE_XLSB = SEED_FOLDER / "ODBC.xlsb"

DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "hr_admin"
DB_PASSWORD = "zbfXZpBPyxgEYEVm"
DB_NAME = "hr_analytics"

# ============================================================================
# ODBC TABLE COLUMNS
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

def convert_excel_date(value):
    """Convert Excel serial date to YYYY-MM-DD format."""
    if pd.isna(value) or value == '' or value is None:
        return None
    
    try:
        # Convert to string and strip whitespace
        value_str = str(value).strip()
        
        # If it's already a date-like string, return as-is
        if '-' in value_str or '/' in value_str:
            return value_str
        
        # Try to convert Excel serial number
        serial = float(value_str)
        
        # Excel date serial starts from 1900-01-01 (serial 1)
        # But Excel incorrectly treats 1900 as a leap year
        from datetime import datetime, timedelta
        
        excel_epoch = datetime(1899, 12, 30)  # Excel's epoch (adjusted for leap year bug)
        converted_date = excel_epoch + timedelta(days=serial)
        
        return converted_date.strftime('%Y-%m-%d')
        
    except (ValueError, TypeError):
        # If conversion fails, return original value
        return value

def load_excel_data(file_path: Path) -> pd.DataFrame:
    """Load Excel file and normalize column names."""
    print(f"📂 Loading Excel file: {file_path.name}")
    
    try:
        # Read Excel file
        engine = 'pyxlsb' if file_path.suffix.lower() == '.xlsb' else None
        df = pd.read_excel(file_path, dtype=str, engine=engine)
        print(f"✓ Loaded {len(df)} rows from Excel")
        
        # Normalize column names to uppercase and strip whitespace
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Convert Excel serial dates to proper date format
        date_columns = [
            'DATE_OF_BIRTH', 'DATE_OF_JOIN', 'ASSIGNMENT_START_DATE', 'ASSIGNMENT_END_DATE',
            'DATE_PROBATION_END', 'CONFIRMED_DATE', 'DATE_OF_DEATH', 'LAST_WORKING_DATE',
            'ACTUAL_TERMINATION_DATE', 'NOTIFIED_TERMINATION_DATE', 'PROJECTED_TERMINATION_DATE',
            'CONTRACT_END_DATE', 'PF_CON_DATE', 'CANCEL_WORK_RELATIONSHIP_DATE'
        ]
        
        for col in date_columns:
            if col in df.columns:
                df[col] = df[col].apply(convert_excel_date)
        
        # Keep only valid ODBC columns
        valid_cols = set(ODBC_COLUMNS)
        original_cols = set(df.columns)
        df = df[[c for c in df.columns if c in valid_cols]]
        
        # Truncate data to fit column limits
        column_limits = {
            'TITLE': 100,
            'NATIONALITY': 100,
            'CNIC_NATIONAL_ID': 100,
            'CONTACT_NUMBER': 100,
            'EMAIL_TYPE': 50,
            'ACTION_CODE': 100,
            'ASSIGNMENT_CATEGORY': 100,
            'DEPARTMENT_TYPE': 100,
            'POSITION_CODE': 100,
            'CADRE': 100,
            'GRADE': 50,
            'CONTRACT_TYPE': 100,
            'DEPT_GROUP': 100,
            'SUB_GROUP': 100,
            'DIVISION': 100,
            'CLUSTERS': 100,
            'REGION': 100,
            'DISTRICT': 100,
            'BRANCH': 100,
            'BRANCH_LEVEL': 50,
            'BRANCH_FLAGSHIP': 50,
            'EMPLOYMENT_STATUS': 100,
            'MANAGER_EMP_NO': 100,
            'MARITAL_STATUS': 100,
            'NOTICE_PERIOD': 50,
            'FESTIVAL_FLAG': 10,
            'GRATUITY': 10,
            'SPI_FLAG': 10,
            'PF_CONVERTED': 10,
            'PF': 10,
            'PF_AMEEN': 10,
            'GPF': 10,
            'PENSION': 10,
            'COMP_ABS': 10,
            'POST_RET_MED': 10,
            'BF': 10,
            'REL_ALL': 10,
            'UNION_MEM': 10,
            'EXTG_FUEL_ENTIT_OR_BMC': 50,
            'CANCEL_WORKRELSHIP_FLAG': 10,
            'PERSON_TYPE': 100,
            'CRC': 50,
            'EXPENSE_POP': 50,
            'LEAVE_FLAG': 10,
        }
        
        for col, limit in column_limits.items():
            if col in df.columns:
                df[col] = df[col].astype(str).apply(lambda x: x[:limit] if len(str(x)) > limit else x)
        
        # Report on columns
        matched_cols = original_cols.intersection(valid_cols)
        ignored_cols = original_cols - valid_cols
        
        print(f"✓ Matched {len(matched_cols)} columns")
        if ignored_cols:
            print(f"⚠ Ignored {len(ignored_cols)} unknown columns")
        
        if df.empty or len(df.columns) == 0:
            raise ValueError("No valid ODBC columns found in the Excel file")
        
        return df
        
    except Exception as e:
        raise Exception(f"Failed to load Excel file: {str(e)}")


def get_database_engine():
    """Create database connection engine."""
    connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    try:
        engine = create_engine(connection_string, echo=False)  # Disable SQL logging
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
            # Truncate table quietly
            conn.execute(text("TRUNCATE TABLE odbc"))
            
            # Insert data in chunks to avoid memory issues and verbose logging
            chunk_size = 1000
            total_rows = len(df)
            
            for i in range(0, total_rows, chunk_size):
                chunk = df.iloc[i:i + chunk_size]
                chunk.to_sql("odbc", con=conn, if_exists="append", index=False, chunksize=1000)
                
                # Show progress for large datasets
                if total_rows > chunk_size:
                    progress = min(i + chunk_size, total_rows)
                    print(f"📥 Inserted {progress}/{total_rows} rows...")
            
            print(f"✅ Successfully inserted {total_rows} rows into ODBC table")
            
    except Exception as e:
        raise Exception(f"Failed to seed ODBC table: {str(e)}")


def main():
    """Main execution function."""
    print("=" * 70)
    print("QUICK ODBC DATA SEEDER")
    print("=" * 70)
    
    # Determine which file to seed
    print("\n📁 Available seed files:")
    files_available = []
    
    if SEED_FILE_XLSX.exists():
        files_available.append(('xlsx', SEED_FILE_XLSX))
        print(f"  [1] {SEED_FILE_XLSX.name} (XLSX)")
    
    if SEED_FILE_XLSB.exists():
        files_available.append(('xlsb', SEED_FILE_XLSB))
        print(f"  [2] {SEED_FILE_XLSB.name} (XLSB)")
    
    if not files_available:
        print("❌ No seed files found in:")
        print(f"   {SEED_FOLDER}")
        sys.exit(1)
    
    # If only one file, use it automatically
    if len(files_available) == 1:
        file_type, seed_file = files_available[0]
        print(f"\n✓ Using: {seed_file.name}")
    else:
        # Ask user to choose
        while True:
            choice = input(f"\nSelect file to seed (1-{len(files_available)}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(files_available):
                file_type, seed_file = files_available[int(choice) - 1]
                print(f"✓ Selected: {seed_file.name}")
                break
            print(f"❌ Invalid choice. Please enter 1-{len(files_available)}")
    
    try:
        # Step 1: Validate file
        print("\n[1/4] Validating file...")
        if not seed_file.exists():
            raise FileNotFoundError(f"Seed file not found: {seed_file}")
        print(f"✓ File found: {seed_file}")
        
        # Step 2: Load Excel data
        print("\n[2/4] Loading Excel data...")
        df = load_excel_data(seed_file)
        
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

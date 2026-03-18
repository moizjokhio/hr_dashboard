import asyncio
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings

def sync_data():
    print("Connecting to database...")
    engine = create_engine(settings.db.SYNC_DATABASE_URL)
    
    with engine.begin() as conn:
        print("Syncing data from odbc to employees...")
        
        # Map columns and insert
        # We use ON CONFLICT DO UPDATE to handle re-runs
        sql = """
        INSERT INTO employees (
            employee_id, full_name, department, grade_level, designation,
            gender, date_of_birth, date_of_joining, basic_salary, status,
            branch_city, branch_country, email, phone
        )
        SELECT
            "EMPLOYEE_NUMBER",
            "FULL_NAME",
            COALESCE("DEPARTMENT", 'Unknown'),
            COALESCE("GRADE", 'N/A'),
            "POS_NAME",
            "GENDER",
            "DATE_OF_BIRTH"::date,
            "HIRE_DATE"::date,
            NULL,
            "USER_STATUS",
            "LOCATION_CODE",
            'Pakistan',
            "EMAIL_ADDRESS",
            NULL
        FROM odbc
        WHERE "EMPLOYEE_NUMBER" IS NOT NULL
        ON CONFLICT (employee_id) DO UPDATE SET
            full_name        = EXCLUDED.full_name,
            department       = EXCLUDED.department,
            grade_level      = EXCLUDED.grade_level,
            designation      = EXCLUDED.designation,
            gender           = EXCLUDED.gender,
            date_of_birth    = EXCLUDED.date_of_birth,
            date_of_joining  = EXCLUDED.date_of_joining,
            basic_salary     = EXCLUDED.basic_salary,
            status           = EXCLUDED.status,
            branch_city      = EXCLUDED.branch_city,
            email            = EXCLUDED.email,
            phone            = EXCLUDED.phone;
        """
        
        try:
            result = conn.execute(text(sql))
            print(f"Synced {result.rowcount} records.")
        except Exception as e:
            print(f"Error syncing data: {e}")

if __name__ == "__main__":
    sync_data()

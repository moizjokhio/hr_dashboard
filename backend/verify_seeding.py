"""Verify DA MIS seeding results"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.db.SYNC_DATABASE_URL)

with engine.connect() as conn:
    # Total records
    total = conn.execute(text("SELECT COUNT(*) FROM da_mis_cases")).scalar()
    print(f"Total records in da_mis_cases: {total}")
    
    # Unique cases
    unique_cases = conn.execute(text("SELECT COUNT(DISTINCT case_number) FROM da_mis_cases")).scalar()
    print(f"Unique case numbers: {unique_cases}")
    
    # Cases with multiple employees
    multi_employee = conn.execute(text("""
        SELECT case_number, COUNT(*) as emp_count 
        FROM da_mis_cases 
        GROUP BY case_number 
        HAVING COUNT(*) > 1
        ORDER BY emp_count DESC
        LIMIT 10
    """)).fetchall()
    
    print(f"\nTop 10 cases with multiple employees:")
    for case_num, count in multi_employee:
        print(f"  Case {case_num}: {count} employees")
    
    # Example: Case 73 details (from your screenshot)
    case_73 = conn.execute(text("""
        SELECT case_number, emp_number, name_of_staff_reported, grade 
        FROM da_mis_cases 
        WHERE case_number = '73.0'
        ORDER BY id
    """)).fetchall()
    
    if case_73:
        print(f"\nCase 73.0 details (should have 3 employees):")
        for row in case_73:
            print(f"  Emp #: {row[1]}, Name: {row[2]}, Grade: {row[3]}")

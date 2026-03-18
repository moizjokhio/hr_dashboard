"""
Seed DA MIS Cases from Excel file
Loads data from 'DA MIS – 2025 (Irfan).xlsx' into da_mis_cases table
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.core.database import Base
from app.models.da_mis_case import DAMISCase


def parse_date(date_value):
    """Parse various date formats"""
    if pd.isna(date_value) or date_value == "" or date_value is None:
        return None
    
    if isinstance(date_value, datetime):
        return date_value.date()
    
    if isinstance(date_value, str):
        try:
            # Try different date formats
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"]:
                try:
                    return datetime.strptime(date_value, fmt).date()
                except ValueError:
                    continue
        except:
            pass
    
    return None


def clean_value(value):
    """Clean and normalize cell values"""
    if pd.isna(value) or value == "" or str(value).strip() == "":
        return None
    return str(value).strip()


def seed_da_mis_cases(excel_file_path: str):
    """
    Seed DA MIS Cases from Excel file
    
    Args:
        excel_file_path: Path to the Excel file
    """
    print(f"Starting DA MIS Cases seeding from: {excel_file_path}")
    
    # Check if file exists
    if not os.path.exists(excel_file_path):
        print(f"ERROR: File not found: {excel_file_path}")
        return
    
    # Create database engine
    engine = create_engine(settings.db.SYNC_DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # Read Excel file
        print("Reading Excel file...")
        df = pd.read_excel(excel_file_path, engine='openpyxl')
        
        # Clean column names (remove extra spaces)
        df.columns = df.columns.str.strip()
        
        print(f"Found {len(df)} rows in Excel file")
        print(f"Columns: {df.columns.tolist()}")
        
        # Column mapping from Excel to database
        # Map EXACT column names as specified
        column_mapping = {
            "Case #": "case_number",
            "S #": "s_number",
            "Emp. #": "emp_number",
            "Name of Staff Reported": "name_of_staff_reported",
            "Grade": "grade",
            "FT": "ft",
            "Branch / Office": "branch_office",
            "Region": "region",
            "Cluster": "cluster",
            "Fixation of Responsibility": "fixation_of_responsibility",
            "Misconduct": "misconduct",
            "Misconduct Category": "misconduct_category",
            "Case Revieved": "case_revieved",
            "Case Received from Audit": "case_received_from_audit",
            "Charge Sheeted Date": "charge_sheeted_date",
            "DAC Decision": "dac_decision",
            "Punishment Implementation": "punishment_implementation",
            "Punishment Letter": "punishment_letter",
            "Year": "year",
            "Quarter": "quarter",
            "Month": "month",
        }
        
        # Check if all required columns exist
        missing_columns = [col for col in column_mapping.keys() if col not in df.columns]
        if missing_columns:
            print(f"WARNING: Missing columns in Excel: {missing_columns}")
            print(f"Available columns: {df.columns.tolist()}")
        
        # Track statistics
        inserted = 0
        skipped = 0
        errors = 0
        
        # Track last valid case number for multi-employee cases
        last_case_number = None
        
        # Process each row
        for idx, row in df.iterrows():
            try:
                # Get case number - if empty, use last valid case number (multi-employee case)
                case_number = clean_value(row.get("Case #"))
                
                if not case_number and last_case_number:
                    # This is an additional employee for the previous case
                    case_number = last_case_number
                    print(f"Row {idx + 2}: Using case # {case_number} from previous row (multi-employee case)")
                elif not case_number:
                    # No case number and no previous case to reference
                    emp_num = clean_value(row.get("Emp. #"))
                    if emp_num:
                        print(f"Row {idx + 2}: Skipping - employee {emp_num} has no Case # and no previous case")
                    else:
                        print(f"Row {idx + 2}: Skipping - empty row")
                    skipped += 1
                    continue
                else:
                    # New case - update last_case_number
                    last_case_number = case_number
                
                # For multi-employee cases, we need to create unique records
                # Check if this exact employee is already in the database for this case
                emp_num = clean_value(row.get("Emp. #"))
                if emp_num:
                    existing = session.query(DAMISCase).filter_by(
                        case_number=case_number,
                        emp_number=emp_num
                    ).first()
                    if existing:
                        print(f"Row {idx + 2}: Skipping - duplicate Case # {case_number} + Emp # {emp_num}")
                        skipped += 1
                        continue
                else:
                    # No employee number - check if case + name combination exists
                    name = clean_value(row.get("Name of Staff Reported"))
                    if name:
                        existing = session.query(DAMISCase).filter_by(
                            case_number=case_number,
                            name_of_staff_reported=name
                        ).first()
                        if existing:
                            print(f"Row {idx + 2}: Skipping - duplicate Case # {case_number} + Name {name}")
                            skipped += 1
                            continue
                
                # Prepare data
                case_data = {}
                for excel_col, db_col in column_mapping.items():
                    if excel_col in df.columns:
                        value = row.get(excel_col)
                        
                        # Special handling for case_number - use the determined case_number, not the row value
                        if db_col == "case_number":
                            case_data[db_col] = case_number
                        # Special handling for dates
                        elif db_col == "charge_sheeted_date":
                            case_data[db_col] = parse_date(value)
                        # Special handling for integers
                        elif db_col == "year":
                            try:
                                if pd.notna(value) and value != "":
                                    case_data[db_col] = int(float(value))
                                else:
                                    case_data[db_col] = None
                            except:
                                case_data[db_col] = None
                        else:
                            case_data[db_col] = clean_value(value)
                
                # Create new case
                new_case = DAMISCase(**case_data)
                session.add(new_case)
                session.commit()
                
                inserted += 1
                if inserted % 100 == 0:
                    print(f"Inserted {inserted} cases...")
                    
            except IntegrityError as e:
                session.rollback()
                print(f"Row {idx + 2}: Integrity error - {str(e)}")
                errors += 1
            except Exception as e:
                session.rollback()
                print(f"Row {idx + 2}: Error - {str(e)}")
                errors += 1
        
        # Print summary
        print("\n" + "="*60)
        print("SEEDING COMPLETE")
        print("="*60)
        print(f"Total rows in file: {len(df)}")
        print(f"Successfully inserted: {inserted}")
        print(f"Skipped (missing/duplicate): {skipped}")
        print(f"Errors: {errors}")
        print("="*60)
        
    except Exception as e:
        print(f"FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    # Default path - adjust as needed
    excel_file = os.path.join(
        os.path.dirname(__file__),
        "..", "Seed_data", "DA MIS - 2025 (Irfan).xlsx"
    )
    
    # Allow command line argument
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
    
    seed_da_mis_cases(excel_file)

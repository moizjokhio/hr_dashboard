"""
Data Upload API endpoints
Allows live refresh of ODBC (employee) data and DA MIS Cases from Excel files.
"""

import io
import os
from datetime import datetime
from time import perf_counter
from typing import Optional

import pandas as pd
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from loguru import logger
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.da_mis_case import DAMISCase

router = APIRouter(tags=["Data Upload"])

# Track last upload timestamps in memory (persists per server process)
_last_upload: dict = {
    "odbc": None,
    "da_cases": None,
}

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

# Date columns in ODBC export
ODBC_DATE_COLS = [
    "DATE_OF_BIRTH", "DATE_OF_JOIN", "ASSIGNMENT_START_DATE",
    "ASSIGNMENT_END_DATE", "DATE_PROBATION_END", "CONFIRMED_DATE",
    "DATE_OF_DEATH", "LAST_WORKING_DATE", "ACTUAL_TERMINATION_DATE",
    "NOTIFIED_TERMINATION_DATE", "PROJECTED_TERMINATION_DATE",
    "PF_CON_DATE", "CANCEL_WORK_RELATIONSHIP_DATE", "CONTRACT_END_DATE",
]

def _read_excel(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Read .xlsx or .xlsb file and return a DataFrame."""
    # Define date columns to parse
    date_cols = [
        "DATE_OF_BIRTH", "DATE_OF_JOIN", "ASSIGNMENT_START_DATE",
        "ASSIGNMENT_END_DATE", "DATE_PROBATION_END", "CONFIRMED_DATE",
        "DATE_OF_DEATH", "LAST_WORKING_DATE", "ACTUAL_TERMINATION_DATE",
        "NOTIFIED_TERMINATION_DATE", "PROJECTED_TERMINATION_DATE",
        "PF_CON_DATE", "CANCEL_WORK_RELATIONSHIP_DATE", "CONTRACT_END_DATE",
    ]
    
    if filename.lower().endswith(".xlsb"):
        # For xlsb, read with dtype=str then convert dates manually
        df = pd.read_excel(io.BytesIO(file_bytes), engine="pyxlsb", dtype=str)
    else:
        # For xlsx, read without dtype to preserve date types, then convert non-dates to string
        df = pd.read_excel(
            io.BytesIO(file_bytes), 
            engine="openpyxl",
            engine_kwargs={'read_only': True}
        )
        
        # Convert date columns to ISO format strings
        for col in df.columns:
            if col.upper() in [d.upper() for d in date_cols]:
                # This is a date column - convert to ISO string
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')
            else:
                # Non-date column - convert to string
                df[col] = df[col].astype(str)

    # Normalise column names
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # Drop rows where ALL columns are empty/null (fixes Excel files with 1M empty rows)
    df = df.dropna(how='all')
    
    # Reset index after dropping rows
    df = df.reset_index(drop=True)
    
    return df


def _clean(value) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip()
    return None if s in ("", "NAN", "NONE", "NAT") else s


def _parse_date(value):
    if value is None:
        return None
    s = str(value).strip()
    if not s or s.upper() in ("NAN", "NONE", "NAT"):
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _copy_dataframe_to_postgres(cursor, df: pd.DataFrame, table_name: str) -> None:
    """Bulk load a dataframe into PostgreSQL using COPY for speed."""
    null_marker = "__NULL__"
    csv_buffer = io.StringIO()
    export_df = df.where(pd.notna(df), null_marker)
    export_df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    quoted_columns = ", ".join(f'"{column}"' for column in export_df.columns)
    copy_sql = (
        f'COPY {table_name} ({quoted_columns}) '
        f"FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL '{null_marker}')"
    )
    cursor.copy_expert(copy_sql, csv_buffer)


# ─────────────────────────────────────────────
# ODBC / Employee data
# ─────────────────────────────────────────────

# Exact column names from the ODBC export (after uppercasing).
# ALL of these must be present in the uploaded file; any missing columns
# will cause the upload to be rejected with a descriptive error.
ODBC_REQUIRED_COLS = {
    "EMPLOYEE_NUMBER", "ASSIGNMENT_NUMBER", "TITLE", "EMPLOYEE_FULL_NAME", "GENDER",
    "DATE_OF_BIRTH", "FATHER_NAME", "NATIONALITY", "CNIC_NATIONAL_ID", "DATE_OF_JOIN",
    "PHONE_TYPE", "CONTACT_NUMBER", "EMAIL_TYPE", "EMAIL_ADDRESS", "ADDRESS_TYPE",
    "HOME_ADDRESS", "BLOOD_GROUP", "RELIGION", "ACTION_CODE", "ASSIGNMENT_START_DATE",
    "ASSIGNMENT_END_DATE", "ASSIGNMENT_CATEGORY", "DATE_PROBATION_END", "PROBATION_DURATION",
    "CONFIRMED_DATE", "DEPARTMENT_NAME", "DEPARTMENT_TYPE", "POSITION_CODE", "POSITION_NAME",
    "CADRE", "GRADE", "LOCATION_NAME", "JOB_NAME", "CONTRACT_TYPE", "DEPT_GROUP",
    "SUB_GROUP", "DIVISION", "CLUSTERS", "REGION", "DISTRICT", "BRANCH", "BRANCH_LEVEL",
    "BRANCH_FLAGSHIP", "EMPLOYMENT_STATUS", "MANAGER_EMP_NAME", "MANAGER_EMP_NO",
    "DATE_OF_DEATH", "MARITAL_STATUS", "LAST_WORKING_DATE", "ACTUAL_TERMINATION_DATE",
    "ACTION_REASON", "NOTIFIED_TERMINATION_DATE", "PROJECTED_TERMINATION_DATE",
    "NOTICE_PERIOD", "GROSS_SALARY", "FESTIVAL_FLAG", "GRATUITY", "SPI_FLAG",
    "PF_CONVERTED", "PF_CON_DATE", "PF", "PF_AMEEN", "GPF", "PENSION", "COMP_ABS",
    "POST_RET_MED", "BF", "REL_ALL", "UNION_MEM", "EXTG_FUEL_ENTIT_OR_BMC",
    "CANCEL_WORKRELSHIP_FLAG", "CANCEL_WORK_RELATIONSHIP_DATE", "CONTRACT_END_DATE",
    "PERSON_TYPE", "CRC", "EXPENSE_POP", "LEAVE_FLAG", "SEQ",
}


@router.post("/odbc")
async def upload_odbc(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload an updated ODBC Excel file (.xlsx or .xlsb).
    Replaces all rows in the `odbc` table then syncs to the `employees` table.
    Returns a summary of rows inserted and sync results.
    """
    ALLOWED = {".xlsx", ".xlsb", ".xls"}
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED)}",
        )

    # Read file
    started_at_full = perf_counter()
    raw = await file.read()
    logger.info(f"📥 Starting ODBC upload: {file.filename} ({len(raw)} bytes)")
    
    upload_start = perf_counter()
    try:
        logger.info(f"📖 Parsing Excel file with pandas...")
        df = _read_excel(raw, file.filename or "upload.xlsx")
        logger.info(f"✅ Excel parsed in {perf_counter() - upload_start:.2f}s - {len(df)} rows found")
    except Exception as e:
        logger.error(f"❌ Excel parsing failed: {e}")
        raise HTTPException(status_code=422, detail=f"Could not read Excel file: {e}")

    # Validate that ALL required columns are present
    file_cols = set(df.columns)
    missing_cols = sorted(ODBC_REQUIRED_COLS - file_cols)
    if missing_cols:
        raise HTTPException(
            status_code=422,
            detail=(
                f"The uploaded file is missing {len(missing_cols)} required column(s): "
                + ", ".join(missing_cols)
                + ". Please upload the standard ODBC export."
            ),
        )
    # Keep only the recognised columns (drops any extra columns silently)
    df = df[[c for c in df.columns if c in ODBC_REQUIRED_COLS]]
    
    # Remove duplicate employee numbers (keep last occurrence)
    initial_rows = len(df)
    df = df.drop_duplicates(subset=['EMPLOYEE_NUMBER'], keep='last')
    duplicates_removed = initial_rows - len(df)
    if duplicates_removed > 0:
        logger.warning(f"⚠️ Removed {duplicates_removed} duplicate employee records (kept latest entry for each employee)")

    # ── Convert Excel serial-number dates to ISO strings ────────────────────
    # xlsb stores dates as floats (days since 1899-12-30); convert them.
    ODBC_DATE_COLS = [
        "DATE_OF_BIRTH", "DATE_OF_JOIN", "ASSIGNMENT_START_DATE",
        "ASSIGNMENT_END_DATE", "DATE_PROBATION_END", "CONFIRMED_DATE",
        "DATE_OF_DEATH", "LAST_WORKING_DATE", "ACTUAL_TERMINATION_DATE",
        "NOTIFIED_TERMINATION_DATE", "PROJECTED_TERMINATION_DATE",
        "PF_CON_DATE", "CANCEL_WORK_RELATIONSHIP_DATE", "CONTRACT_END_DATE",
    ]

    def _excel_serial_to_date(val):
        """Convert an Excel date serial or a date string to a date object or None."""
        if val is None:
            return None
        s = str(val).strip()
        if s == "" or s.upper() in ("NAN", "NONE", "NAT"):
            return None
        
        # Try numeric serial first
        try:
            serial = float(s)
            # Excel epoch is 1899-12-30; adjust for the leap-year bug (serial 60)
            from datetime import date, timedelta
            epoch = date(1899, 12, 30)
            return (epoch + timedelta(days=int(serial))).isoformat()
        except ValueError:
            pass
        
        # Try common string formats
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%Y-%m-%d %H:%M:%S", "%d-%b-%Y", "%d-%B-%Y"):
            try:
                from datetime import datetime
                parsed = datetime.strptime(s, fmt).date()
                return parsed.isoformat()
            except ValueError:
                continue
        
        return None  # unparseable → store NULL

    date_convert_start = perf_counter()
    dates_converted = 0
    dates_null = 0
    
    for col in ODBC_DATE_COLS:
        if col in df.columns:
            # Count non-null values before conversion
            non_null_before = df[col].notna().sum()
            df[col] = df[col].apply(_excel_serial_to_date)
            # Count non-null after
            non_null_after = df[col].notna().sum()
            dates_converted += non_null_after
            dates_null += (len(df) - non_null_after)
    
    logger.info(f"📅 Date conversion completed in {perf_counter() - date_convert_start:.2f}s - {dates_converted} dates converted, {dates_null} null dates")
    # ────────────────────────────────────────────────────────────────────────

    total_rows = len(df)

    # Reload the odbc table and rebuild employees inside one transaction.
    # COPY is much faster than `to_sql()` for large ODBC exports.
    sync_sql = """
        INSERT INTO employees (
            employee_id,
            full_name,
            department,
            unit_name,
            grade_level,
            designation,
            employment_type,
            branch_city,
            branch_country,
            date_of_birth,
            date_of_joining,
            years_of_experience,
            gender,
            marital_status,
            religion,
            basic_salary,
            total_monthly_salary,
            reporting_manager_id,
            status,
            email,
            phone
        )
        SELECT
            "EMPLOYEE_NUMBER",
            COALESCE(NULLIF("EMPLOYEE_FULL_NAME", ''), 'Unknown'),
            COALESCE(NULLIF("DEPARTMENT_NAME", ''), 'Unknown'),
            COALESCE(NULLIF("SUB_GROUP", ''), 'Unknown'),
            COALESCE(NULLIF("GRADE", ''), 'N/A'),
            NULLIF("POSITION_NAME", ''),
            NULLIF("CONTRACT_TYPE", ''),
            NULLIF("LOCATION_NAME", ''),
            'Pakistan',
            "DATE_OF_BIRTH"::date,
            "DATE_OF_JOIN"::date,
            NULL,
            NULLIF("GENDER", ''),
            NULLIF("MARITAL_STATUS", ''),
            NULLIF("RELIGION", ''),
            NULLIF(REGEXP_REPLACE(COALESCE("GROSS_SALARY"::text, ''), '[^0-9.\-]', '', 'g'), '')::double precision,
            NULLIF(REGEXP_REPLACE(COALESCE("GROSS_SALARY"::text, ''), '[^0-9.\-]', '', 'g'), '')::double precision,
            NULLIF("MANAGER_EMP_NO", ''),
            NULLIF("EMPLOYMENT_STATUS", ''),
            NULLIF("EMAIL_ADDRESS", ''),
            NULLIF("CONTACT_NUMBER", '')
        FROM odbc
        WHERE NULLIF("EMPLOYEE_NUMBER", '') IS NOT NULL;
    """

    synced_rows = 0
    processing_seconds = 0.0
    try:
        from sqlalchemy import create_engine
        from app.core.config import settings

        db_started_at = perf_counter()
        logger.info(f"💾 Starting database operations...")
        engine = create_engine(settings.db.SYNC_DATABASE_URL)
        raw_conn = engine.raw_connection()
        try:
            with raw_conn.cursor() as cursor:
                logger.info(f"🗑️ Truncating existing data...")
                cursor.execute('TRUNCATE TABLE odbc, employees RESTART IDENTITY CASCADE')
                logger.info(f"⬆️ Bulk loading {total_rows} rows via COPY...")
                _copy_dataframe_to_postgres(cursor, df, 'odbc')
                logger.info(f"🔄 Syncing to employees table...")
                cursor.execute(sync_sql)
                synced_rows = cursor.rowcount or 0

            raw_conn.commit()
            processing_seconds = round(perf_counter() - started_at_full, 2)
            logger.info(f"✅ Upload complete in {processing_seconds}s - {synced_rows} employees synced")
        except Exception:
            raw_conn.rollback()
            raise
        finally:
            raw_conn.close()
            engine.dispose()
    except Exception as e:
        logger.error(f"❌ Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error while loading ODBC data: {e}")

    _last_upload["odbc"] = datetime.utcnow().isoformat() + "Z"

    return {
        "status": "success",
        "data_source": "odbc",
        "filename": file.filename,
        "rows_in_file": total_rows,
        "rows_loaded_to_odbc": total_rows,
        "employees_synced": synced_rows,
        "sync_error": None,
        "processing_seconds": processing_seconds,
        "uploaded_at": _last_upload["odbc"],
    }


# ─────────────────────────────────────────────
# DA MIS Cases
# ─────────────────────────────────────────────

DA_COLUMN_MAPPING = {
    "CASE #": "case_number",
    "S #": "s_number",
    "EMP. #": "emp_number",
    "NAME OF STAFF REPORTED": "name_of_staff_reported",
    "GRADE": "grade",
    "FT": "ft",
    "BRANCH / OFFICE": "branch_office",
    "REGION": "region",
    "CLUSTER": "cluster",
    "FIXATION OF RESPONSIBILITY": "fixation_of_responsibility",
    "MISCONDUCT": "misconduct",
    "MISCONDUCT CATEGORY": "misconduct_category",
    "CASE REVIEVED": "case_revieved",
    "CASE RECEIVED FROM AUDIT": "case_received_from_audit",
    "CHARGE SHEETED DATE": "charge_sheeted_date",
    "DAC DECISION": "dac_decision",
    "PUNISHMENT IMPLEMENTATION": "punishment_implementation",
    "PUNISHMENT LETTER": "punishment_letter",
    "YEAR": "year",
    "QUARTER": "quarter",
    "MONTH": "month",
}


@router.post("/da-cases")
async def upload_da_cases(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload an updated DA MIS Cases Excel file (.xlsx).
    Replaces ALL existing DA cases with the contents of the uploaded file.
    Returns a summary with counts of inserted / skipped / error rows.
    """
    ALLOWED = {".xlsx", ".xls"}
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED)}",
        )

    raw = await file.read()
    try:
        df = pd.read_excel(io.BytesIO(raw), dtype=str)
        df.columns = df.columns.str.strip()
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not read Excel file: {e}")

    # Map columns (case-insensitive)
    upper_col_map = {k.upper(): v for k, v in DA_COLUMN_MAPPING.items()}
    df.columns = [str(c).strip() for c in df.columns]
    col_remap = {c: upper_col_map[c.upper()] for c in df.columns if c.upper() in upper_col_map}

    if not col_remap:
        raise HTTPException(
            status_code=422,
            detail="No recognised DA MIS columns found. "
                   "Please upload the standard DA MIS export.",
        )

    # Wipe existing data
    try:
        db.query(DAMISCase).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear existing DA cases: {e}")

    inserted = skipped = errors = 0
    last_case_number = None
    cases_to_insert = []

    for idx, row in df.iterrows():
        try:
            raw_case = _clean(row.get("Case #") or row.get("CASE #"))

            if not raw_case and last_case_number:
                raw_case = last_case_number
            elif not raw_case:
                emp = _clean(row.get("Emp. #") or row.get("EMP. #"))
                if emp:
                    skipped += 1
                continue
            else:
                last_case_number = raw_case

            case_data: dict = {}
            for excel_col, db_col in col_remap.items():
                value = row.get(excel_col)
                if db_col == "case_number":
                    case_data[db_col] = raw_case
                elif db_col == "charge_sheeted_date":
                    case_data[db_col] = _parse_date(_clean(value))
                elif db_col == "year":
                    v = _clean(value)
                    try:
                        case_data[db_col] = int(float(v)) if v else None
                    except Exception:
                        case_data[db_col] = None
                else:
                    case_data[db_col] = _clean(value)

            cases_to_insert.append(DAMISCase(**case_data))
            
            # Batch size of 1000 to prevent memory blow up
            if len(cases_to_insert) >= 1000:
                try:
                    db.bulk_save_objects(cases_to_insert)
                    db.commit()
                    inserted += len(cases_to_insert)
                except Exception as e:
                    db.rollback()
                    errors += len(cases_to_insert)
                finally:
                    cases_to_insert = []
                
        except Exception as e:
            # Error during single row data parsing
            errors += 1
            pass

    # Insert remaining records
    if cases_to_insert:
        try:
            db.bulk_save_objects(cases_to_insert)
            db.commit()
            inserted += len(cases_to_insert)
        except Exception as e:
            db.rollback()
            errors += len(cases_to_insert)

    _last_upload["da_cases"] = datetime.utcnow().isoformat() + "Z"

    return {
        "status": "success",
        "data_source": "da_cases",
        "filename": file.filename,
        "rows_in_file": len(df),
        "rows_inserted": inserted,
        "rows_skipped": skipped,
        "rows_error": errors,
        "uploaded_at": _last_upload["da_cases"],
    }


# ─────────────────────────────────────────────
# Status endpoint
# ─────────────────────────────────────────────

@router.get("/status")
def upload_status():
    """
    Returns the last successful upload timestamp for each data source.
    """
    return {
        "odbc": {
            "last_uploaded_at": _last_upload["odbc"],
            "description": "Employee / ODBC master data",
        },
        "da_cases": {
            "last_uploaded_at": _last_upload["da_cases"],
            "description": "Disciplinary Action MIS cases",
        },
    }

"""Seed PostgreSQL tables from Excel files.

Replace the placeholder paths below with your Excel file locations, then run:

    python scripts/seed_from_excel.py --odbc --total-experience

Optional flags:
    --odbc PATH_TO_FILE.xlsx
    --total-experience PATH_TO_FILE.xlsx

This script truncates the target tables before inserting data.
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

# Allow importing the app settings
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))
from app.core.config import settings  # noqa: E402

# Placeholder paths: update these to your actual Excel file locations
DEFAULT_ODBC_PATH = Path(r"C:\\path\\to\\odbc.xlsx")
DEFAULT_TOTAL_EXP_PATH = Path(r"C:\\path\\to\\total_experience.xlsx")


def _load_excel(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Excel file not found: {path}. Replace the placeholder path in seed_from_excel.py."
        )
    df = pd.read_excel(path, dtype=str)
    # Normalize column names to uppercase to match table definitions
    df.columns = [str(c).strip().upper() for c in df.columns]
    return df


def seed_odbc(path: Path, engine) -> None:
    df = _load_excel(path)
    # Keep only columns that exist in the actual ODBC export
    valid_cols = set([
        "EMPLOYEE_NUMBER", "FULL_NAME", "DATE_OF_BIRTH", "MARITAL_STATUS", "NATIONALITY",
        "BLOOD_TYPE", "GENDER", "NATIONAL_IDENTIFIER", "HIRE_DATE", "PROB_END_DATE",
        "CONFIIRMATION_DATE", "EMPLOYMENT_CATEGORY", "GRADE", "POSITION", "GROUP", "SUB_GROUP",
        "ORG", "CRC", "EMAIL_ADDRESS", "USER_STATUS", "LEAVING_REASON", "ACTUAL_TERMINATION_DATE",
        "NOTIFIED_TERMINATION_DATE", "PROJECTED_TERMINATION_DATE", "ACCOUNT_NUMBER", "TITLE",
        "FATHER_NAME", "CADRE", "EXPENSE_POP", "JOB", "SUPERVISOR", "PF", "PF_CONVERTED",
        "PF_CON_DATE", "PF_AMEEN", "GRATUITY", "GPF", "PENSION", "COMP_ABS", "POST_RET_MED",
        "BF", "REL_ALL", "UNION_MEM", "GRD_FUEL_ADJ_OR_BMC", "FESTIVAL_PART_OF_GROSS",
        "DATE_OF_DEATH", "PROBATION_PERIOD", "POP_CODE", "LOCATION_CODE", "PERSON_ID",
        "LAST_WORKING_DAY", "POSITION_ID", "BRANCH_CATEGORY", "DEPARTMENT", "CLUS",
        "POS_NAME", "REGION",
    ])
    df = df[[c for c in df.columns if c in valid_cols]]

    with engine.begin() as conn:
        # replace drops+recreates so schema always matches the actual file
        df.to_sql("odbc", con=conn, if_exists="replace", index=False, method="multi")


def seed_total_experience(path: Path, engine) -> None:
    df = _load_excel(path)
    valid_cols = set([
        "EMPLOYEE_NUMBER", "TITLE", "FULL_NAME", "GRADE", "HIRING DATE", "USER_STATUS",
        "TOTAL EXPERIENCE", "PREVIOUS EMPLOYER", "POSTION",
    ])
    # Normalize specific column names to match table definitions
    rename_map = {
        "HIRING DATE": "Hiring_date",
        "TOTAL EXPERIENCE": "Total_Experience",
        "PREVIOUS EMPLOYER": "Previous_Employer",
        "GRADE": "Grade",
        "POSTION": "Postion",
    }
    df = df[[c for c in df.columns if c in valid_cols]]
    df = df.rename(columns=rename_map)

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE total_experience"))
        df.to_sql("total_experience", con=conn, if_exists="append", index=False, method="multi")


def main():
    parser = argparse.ArgumentParser(description="Seed tables from Excel")
    parser.add_argument("--odbc", dest="odbc_path", type=Path, default=DEFAULT_ODBC_PATH,
                        help="Path to ODBC Excel file")
    parser.add_argument("--total-experience", dest="total_exp_path", type=Path, default=DEFAULT_TOTAL_EXP_PATH,
                        help="Path to total experience Excel file")
    parser.add_argument("--skip-odbc", action="store_true", help="Skip seeding ODBC table")
    parser.add_argument("--skip-total", action="store_true", help="Skip seeding total_experience table")
    args = parser.parse_args()

    engine = create_engine(settings.db.SYNC_DATABASE_URL)

    if not args.skip_odbc:
        seed_odbc(args.odbc_path, engine)
        print(f"Seeded odbc from {args.odbc_path}")

    if not args.skip_total:
        seed_total_experience(args.total_exp_path, engine)
        print(f"Seeded total_experience from {args.total_exp_path}")


if __name__ == "__main__":
    main()

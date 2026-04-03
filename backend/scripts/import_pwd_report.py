"""
Import PWD employee data from an Excel report into PostgreSQL.

Usage:
  python backend/scripts/import_pwd_report.py \
    --file "Disability Report (2)-1775225322597-478338689.xlsx"

  python backend/scripts/import_pwd_report.py \
    --file "Disability Report (2)-1775225322597-478338689.xlsx" \
    --database-url "postgresql://..."

Notes:
- If --database-url is omitted, DATABASE_URL is used.
- Data is upserted by person_number, so repeated runs are safe.
"""

from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values


TABLE_SQL = """
CREATE TABLE IF NOT EXISTS public.pwd_employees (
    person_number TEXT PRIMARY KEY,
    full_name TEXT,
    user_status TEXT,
    date_of_birth DATE,
    group_name TEXT,
    sub_group TEXT,
    cluster TEXT,
    region TEXT,
    hire_date DATE,
    organization_name TEXT,
    job_name TEXT,
    position_name TEXT,
    grade_name TEXT,
    location_name TEXT,
    gender TEXT,
    nature_of_disability TEXT,
    category TEXT,
    ailment TEXT,
    effective_start_date DATE,
    disclosure_date DATE,
    source_file TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


UPSERT_SQL = """
INSERT INTO public.pwd_employees (
    person_number,
    full_name,
    user_status,
    date_of_birth,
    group_name,
    sub_group,
    cluster,
    region,
    hire_date,
    organization_name,
    job_name,
    position_name,
    grade_name,
    location_name,
    gender,
    nature_of_disability,
    category,
    ailment,
    effective_start_date,
    disclosure_date,
    source_file
)
VALUES %s
ON CONFLICT (person_number) DO UPDATE SET
    full_name = EXCLUDED.full_name,
    user_status = EXCLUDED.user_status,
    date_of_birth = EXCLUDED.date_of_birth,
    group_name = EXCLUDED.group_name,
    sub_group = EXCLUDED.sub_group,
    cluster = EXCLUDED.cluster,
    region = EXCLUDED.region,
    hire_date = EXCLUDED.hire_date,
    organization_name = EXCLUDED.organization_name,
    job_name = EXCLUDED.job_name,
    position_name = EXCLUDED.position_name,
    grade_name = EXCLUDED.grade_name,
    location_name = EXCLUDED.location_name,
    gender = EXCLUDED.gender,
    nature_of_disability = EXCLUDED.nature_of_disability,
    category = EXCLUDED.category,
    ailment = EXCLUDED.ailment,
    effective_start_date = EXCLUDED.effective_start_date,
    disclosure_date = EXCLUDED.disclosure_date,
    source_file = EXCLUDED.source_file,
    updated_at = NOW();
"""


COLUMN_MAP = {
    "PERSON NUMBER": "person_number",
    "FULL NAME": "full_name",
    "USER STATUS": "user_status",
    "DATE OF BIRTH": "date_of_birth",
    "GROUP": "group_name",
    "SUB GROUP": "sub_group",
    "CLUSTER": "cluster",
    "REGION": "region",
    "HIRE DATE": "hire_date",
    "ORGANIZATION NAME": "organization_name",
    "JOB NAME": "job_name",
    "POSITION NAME": "position_name",
    "GRADE NAME": "grade_name",
    "LOCATION NAME": "location_name",
    "GENDER": "gender",
    "NATURE OF DISABILITY": "nature_of_disability",
    "CATEGORY": "category",
    "AILMENT": "ailment",
    "EFFECTIVE START DATE": "effective_start_date",
    "DISCLOSURE DATE": "disclosure_date",
}

DATE_COLUMNS = {
    "date_of_birth",
    "hire_date",
    "effective_start_date",
    "disclosure_date",
}


@dataclass
class PwdRecord:
    person_number: str
    full_name: Optional[str]
    user_status: Optional[str]
    date_of_birth: Optional[date]
    group_name: Optional[str]
    sub_group: Optional[str]
    cluster: Optional[str]
    region: Optional[str]
    hire_date: Optional[date]
    organization_name: Optional[str]
    job_name: Optional[str]
    position_name: Optional[str]
    grade_name: Optional[str]
    location_name: Optional[str]
    gender: Optional[str]
    nature_of_disability: Optional[str]
    category: Optional[str]
    ailment: Optional[str]
    effective_start_date: Optional[date]
    disclosure_date: Optional[date]
    source_file: str


def normalize_col_name(value: str) -> str:
    return re.sub(r"\s+", " ", str(value).strip().upper())


def clean_text(value: object) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.upper() in {"NAN", "NAT", "NONE"}:
        return None
    return text


def clean_person_number(value: object) -> Optional[str]:
    text = clean_text(value)
    if not text:
        return None

    # Keep only digits because report values can include hidden formatting marks.
    digits = re.sub(r"\D", "", text)
    return digits or None


def parse_date(value: object) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, pd.Timestamp):
        if pd.isna(value):
            return None
        return value.date()

    text = clean_text(value)
    if not text:
        return None

    parsed = pd.to_datetime(text, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date()


def split_prefixed_label(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    return re.sub(r"^\d+\.", "", value).strip() or value


def load_excel(file_path: Path) -> pd.DataFrame:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_excel(file_path, engine="openpyxl")
    df.columns = [normalize_col_name(c) for c in df.columns]
    df = df.dropna(how="all").reset_index(drop=True)
    return df


def map_records(df: pd.DataFrame, source_file: str) -> list[PwdRecord]:
    missing = [c for c in COLUMN_MAP if c not in df.columns]
    if missing:
        raise ValueError(
            "PWD report is missing required columns: " + ", ".join(sorted(missing))
        )

    renamed = df.rename(columns=COLUMN_MAP)
    renamed = renamed[[*COLUMN_MAP.values()]]

    records_by_person: dict[str, PwdRecord] = {}

    for _, row in renamed.iterrows():
        person_number = clean_person_number(row.get("person_number"))
        if not person_number:
            continue

        payload = {}
        for col in renamed.columns:
            raw_value = row.get(col)
            if col in DATE_COLUMNS:
                payload[col] = parse_date(raw_value)
            else:
                payload[col] = clean_text(raw_value)

        # Keep labels readable in charts by removing source numeric prefixes.
        payload["group_name"] = split_prefixed_label(payload.get("group_name"))
        payload["sub_group"] = split_prefixed_label(payload.get("sub_group"))
        payload["cluster"] = split_prefixed_label(payload.get("cluster"))
        payload["region"] = split_prefixed_label(payload.get("region"))
        payload["position_name"] = split_prefixed_label(payload.get("position_name"))

        records_by_person[person_number] = PwdRecord(
            person_number=person_number,
            full_name=payload.get("full_name"),
            user_status=payload.get("user_status"),
            date_of_birth=payload.get("date_of_birth"),
            group_name=payload.get("group_name"),
            sub_group=payload.get("sub_group"),
            cluster=payload.get("cluster"),
            region=payload.get("region"),
            hire_date=payload.get("hire_date"),
            organization_name=payload.get("organization_name"),
            job_name=payload.get("job_name"),
            position_name=payload.get("position_name"),
            grade_name=payload.get("grade_name"),
            location_name=payload.get("location_name"),
            gender=payload.get("gender"),
            nature_of_disability=payload.get("nature_of_disability"),
            category=payload.get("category"),
            ailment=payload.get("ailment"),
            effective_start_date=payload.get("effective_start_date"),
            disclosure_date=payload.get("disclosure_date"),
            source_file=source_file,
        )

    return list(records_by_person.values())


def chunked(items: list[PwdRecord], size: int) -> Iterable[list[PwdRecord]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def upsert_records(database_url: str, records: list[PwdRecord]) -> int:
    if not records:
        return 0

    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(TABLE_SQL)

            for batch in chunked(records, 500):
                values = [
                    (
                        r.person_number,
                        r.full_name,
                        r.user_status,
                        r.date_of_birth,
                        r.group_name,
                        r.sub_group,
                        r.cluster,
                        r.region,
                        r.hire_date,
                        r.organization_name,
                        r.job_name,
                        r.position_name,
                        r.grade_name,
                        r.location_name,
                        r.gender,
                        r.nature_of_disability,
                        r.category,
                        r.ailment,
                        r.effective_start_date,
                        r.disclosure_date,
                        r.source_file,
                    )
                    for r in batch
                ]
                execute_values(cursor, UPSERT_SQL, values)

        conn.commit()

    return len(records)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import PWD report into PostgreSQL")
    parser.add_argument("--file", required=True, type=Path, help="Path to disability report (.xlsx)")
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", ""),
        help="Target PostgreSQL URL (defaults to DATABASE_URL env var)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.database_url:
        raise RuntimeError("Missing database URL. Set DATABASE_URL or pass --database-url.")

    df = load_excel(args.file)
    records = map_records(df, source_file=args.file.name)
    count = upsert_records(args.database_url, records)

    print(f"Imported/updated {count} PWD row(s) from {args.file.name}")


if __name__ == "__main__":
    main()

"""
Sync local PostgreSQL database to Supabase PostgreSQL.

Usage (PowerShell):
  $env:LOCAL_DATABASE_URL="postgresql://hr_admin:your_local_password@localhost:5432/hr_analytics"
  $env:SUPABASE_DATABASE_URL="postgresql://postgres.your_ref:your_db_password@aws-0-region.pooler.supabase.com:6543/postgres?sslmode=require"
  python backend/scripts/sync_local_to_supabase.py

Notes:
- This script truncates destination tables before inserting data.
- It skips PostgreSQL internal tables and keeps table structure managed by Alembic/migrations.
"""

from __future__ import annotations

import io
import os
from typing import List

import psycopg2
from psycopg2 import sql

EXCLUDED_TABLES = {"alembic_version"}


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _get_tables(conn) -> List[str]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT tablename
            FROM pg_catalog.pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
            """
        )
        tables = [row[0] for row in cur.fetchall()]
    return [t for t in tables if t not in EXCLUDED_TABLES]


def _truncate_destination(conn, tables: List[str]) -> None:
    if not tables:
        return
    with conn.cursor() as cur:
        identifiers = [sql.Identifier("public", t) for t in tables]
        query = sql.SQL("TRUNCATE TABLE {} RESTART IDENTITY CASCADE").format(
            sql.SQL(", ").join(identifiers)
        )
        cur.execute(query)
    conn.commit()


def _copy_table_data(src_conn, dst_conn, table: str) -> int:
    buffer = io.StringIO()
    with src_conn.cursor() as src_cur:
        src_cur.copy_expert(
            sql.SQL("COPY {} TO STDOUT WITH CSV HEADER").format(
                sql.Identifier("public", table)
            ).as_string(src_conn),
            buffer,
        )

    buffer.seek(0)

    with dst_conn.cursor() as dst_cur:
        dst_cur.copy_expert(
            sql.SQL("COPY {} FROM STDIN WITH CSV HEADER").format(
                sql.Identifier("public", table)
            ).as_string(dst_conn),
            buffer,
        )

        dst_cur.execute(
            sql.SQL("SELECT COUNT(*) FROM {} ").format(sql.Identifier("public", table))
        )
        row_count = int(dst_cur.fetchone()[0])

    dst_conn.commit()
    return row_count


def main() -> None:
    local_url = _require_env("LOCAL_DATABASE_URL")
    supabase_url = _require_env("SUPABASE_DATABASE_URL")

    print("Connecting to local and Supabase databases...")

    with psycopg2.connect(local_url) as src_conn, psycopg2.connect(supabase_url) as dst_conn:
        src_conn.autocommit = False
        dst_conn.autocommit = False

        tables = _get_tables(src_conn)
        if not tables:
            print("No tables found in local public schema.")
            return

        print(f"Found {len(tables)} table(s): {', '.join(tables)}")
        print("Truncating destination tables...")
        _truncate_destination(dst_conn, tables)

        total_rows = 0
        for table in tables:
            count = _copy_table_data(src_conn, dst_conn, table)
            total_rows += count
            print(f"Synced table '{table}' with {count} row(s)")

        print(f"Sync complete. Total rows copied: {total_rows}")


if __name__ == "__main__":
    main()

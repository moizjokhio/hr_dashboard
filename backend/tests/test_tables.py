"""Basic tests for new PostgreSQL tables and seeding hooks.

These tests are lightweight and will skip automatically if a database
connection is not available. They are intended to validate that:
- The Alembic migration created the target tables (`odbc`, `total_experience`).
- The Excel seeding helper raises a clear error when the placeholder path is unchanged.
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from scripts import seed_from_excel
from app.core.config import settings


@pytest.fixture(scope="module")
def engine():
    try:
        eng = create_engine(settings.db.SYNC_DATABASE_URL)
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        return eng
    except OperationalError:
        pytest.skip("PostgreSQL is not available; skipping DB-dependent tests.")


def _table_exists(engine, table_name: str) -> bool:
    query = text("SELECT to_regclass(:tbl) IS NOT NULL")
    with engine.connect() as conn:
        return conn.execute(query, {"tbl": f"public.{table_name}"}).scalar()


def test_odbc_table_exists(engine):
    assert _table_exists(engine, "odbc"), "Table 'odbc' should exist after migration."


def test_total_experience_table_exists(engine):
    assert _table_exists(engine, "total_experience"), "Table 'total_experience' should exist after migration."


def test_placeholder_paths_raise_file_not_found():
    with pytest.raises(FileNotFoundError):
        seed_from_excel._load_excel(seed_from_excel.DEFAULT_ODBC_PATH)
    with pytest.raises(FileNotFoundError):
        seed_from_excel._load_excel(seed_from_excel.DEFAULT_TOTAL_EXP_PATH)

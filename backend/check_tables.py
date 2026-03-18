"""Check if table exists"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings

engine = create_engine(settings.db.SYNC_DATABASE_URL)

inspector = inspect(engine)
tables = inspector.get_table_names()

print(f"All tables: {tables}")
print(f"\nda_mis_cases exists: {'da_mis_cases' in tables}")

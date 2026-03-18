"""Reset DA MIS Cases table"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.db.SYNC_DATABASE_URL)

with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS da_mis_cases CASCADE"))
    conn.commit()
    print("DA MIS Cases table dropped successfully")

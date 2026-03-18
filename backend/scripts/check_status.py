import sys
from pathlib import Path
from sqlalchemy import create_engine, text
import pandas as pd

# Add backend directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings

def check_status():
    engine = create_engine(settings.db.SYNC_DATABASE_URL)
    with engine.connect() as conn:
        df = pd.read_sql("SELECT status, count(*) as count FROM employees GROUP BY status", conn)
        print(df)

if __name__ == "__main__":
    check_status()

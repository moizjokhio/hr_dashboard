"""Standalone NLP test without FastAPI imports"""
import asyncio
import os
import sys
from pathlib import Path

# Set up path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment before importing anything
os.environ.setdefault("ENVIRONMENT", "development")

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text


async def test_single_query():
    """Test single query with minimal imports"""
    
    # Create engine directly
    DATABASE_URL = "postgresql+asyncpg://postgres:Nadra%4012345@localhost:5432/hr_analytics"
    
    async_engine = create_async_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    
    query_text = "Show me all departments in UBL Head Office location"
    print(f"Testing query: {query_text}\n")
    print("Expected SQL: SELECT DISTINCT department FROM odbc WHERE \"LOCATION_NAME\" LIKE '%UBL Head Office%'\n")
    
    async with AsyncSession(async_engine, expire_on_commit=False) as session:
        try:
            # Import only what we need
            from app.ml.nlp_query_service import NLPQueryService
            
            nlp = NLPQueryService(session=session)
            response = await nlp.process_query(query=query_text)
            
            print(f"Success: {response.success}")
            print(f"Generated SQL: {response.generated_sql.raw_sql if response.generated_sql else 'None'}")
            print(f"Row count: {response.row_count}")
            
            if response.success and response.data:
                print(f"\n=== Results ({len(response.data)} rows) ===")
                for i, row in enumerate(response.data[:10], 1):
                    print(f"  {i}. {row}")
                if len(response.data) > 10:
                    print(f"  ... and {len(response.data) - 10} more rows")
            elif not response.success:
                print(f"\nError: {response.analysis}")
                
        except Exception as e:
            await session.rollback()
            print(f"\nException occurred: {e}")
            import traceback
            traceback.print_exc()
    
    await async_engine.dispose()
    print("\nTest complete")


if __name__ == "__main__":
    asyncio.run(test_single_query())
